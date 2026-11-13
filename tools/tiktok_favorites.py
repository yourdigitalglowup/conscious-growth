"""Hämta transkript för de senaste AI-videorna bland sparade TikTok-videor.

Användning:
    python tools/tiktok_favorites.py <tiktok-export.json eller .zip eller länkfil.txt> [antal=50] [utmapp]

- Läser TikToks dataexport (JSON) och hittar listan med favoritvideor (sparade).
  Fungerar också med en vanlig textfil med en TikTok-länk per rad.
- Går igenom videorna från nyast till äldst och behåller de som handlar om AI
  (avgörs av beskrivning och hashtaggar) tills `antal` videor hittats.
- Använder TikToks egna undertexter; saknas de transkriberas ljudet lokalt med Whisper.
- Skriver en markdown-fil med alla transkript. Inga AI-tokens används i något steg.

Kräver: yt-dlp, ffmpeg och (för videor utan undertext) openai-whisper.
"""
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

AI_WORDS = re.compile(
    r"\b(ai|a\.i\.|artificial intelligence|artificiell intelligens|chatgpt|gpt[-\s]?\d*|openai|claude|"
    r"anthropic|gemini|llm|llms|copilot|midjourney|automation|automations|automatisering|agent|agents|"
    r"agentic|prompt|prompts|prompting|n8n|make\.com|zapier|cursor|vibe ?coding|machine learning|"
    r"perplexity|grok|deepseek|ollama|hugging ?face|aitools|aitool|aiagents|aibusiness)\b",
    re.I,
)


def load_export(path):
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = next(n for n in z.namelist() if n.endswith(".json"))
            return json.loads(z.read(name))
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_links": re.findall(r"https?://\S*tiktok\.com\S*", text)}


def find_favorites(node, inside_fav=False):
    """Letar rekursivt upp poster med 'Link' under en nyckel som innehåller 'Favorite'."""
    found = []
    if isinstance(node, dict):
        for k, v in node.items():
            fav = inside_fav or "favorite" in k.lower()
            if fav and isinstance(v, list) and v and isinstance(v[0], dict) and any(
                key.lower() in ("link", "url") for key in v[0]
            ):
                for item in v:
                    link = item.get("Link") or item.get("link") or item.get("Url") or item.get("url")
                    if link:
                        found.append({"date": item.get("Date") or item.get("date") or "", "link": link})
            else:
                found += find_favorites(v, fav)
    elif isinstance(node, list):
        for v in node:
            found += find_favorites(v, inside_fav)
    return found


def get_items(data):
    if "_links" in data:
        return [{"date": "", "link": l} for l in data["_links"]]
    items = find_favorites(data)
    items.sort(key=lambda x: x["date"], reverse=True)  # nyast först
    seen, out = set(), []
    for it in items:
        if it["link"] not in seen:
            seen.add(it["link"])
            out.append(it)
    return out


def ytdlp(args, cwd):
    return subprocess.run(["yt-dlp", "--no-warnings", *args], cwd=cwd, capture_output=True, text=True)


def vtt_to_text(path):
    lines = []
    for l in open(path, encoding="utf-8"):
        l = l.strip()
        if not l or l == "WEBVTT" or "-->" in l or re.fullmatch(r"\d+", l):
            continue
        if not lines or lines[-1] != l:
            lines.append(l)
    return " ".join(lines)


def whisper_text(link, work):
    r = ytdlp(["-q", "-x", "--audio-format", "mp3", "-o", "audio.%(ext)s", link], work)
    audio = os.path.join(work, "audio.mp3")
    if not os.path.exists(audio):
        return ""
    subprocess.run(
        ["whisper", audio, "--model", "small", "--output_format", "txt", "--output_dir", work, "--fp16", "False"],
        capture_output=True,
    )
    txt = os.path.join(work, "audio.txt")
    return " ".join(open(txt, encoding="utf-8").read().split()) if os.path.exists(txt) else ""


def main():
    src = sys.argv[1]
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    outdir = sys.argv[3] if len(sys.argv) > 3 else "research/sparade-ai-videor"
    os.makedirs(outdir, exist_ok=True)
    items = get_items(load_export(src))
    print(f"{len(items)} sparade videor hittades i exporten")

    results, checked, failed = [], 0, 0
    for it in items:
        if len(results) >= want:
            break
        checked += 1
        with tempfile.TemporaryDirectory() as work:
            r = ytdlp(["--skip-download", "--write-info-json", "--write-subs", "--write-auto-subs",
                       "--sub-langs", "all", "-o", "v.%(ext)s", it["link"]], work)
            info_p = os.path.join(work, "v.info.json")
            if not os.path.exists(info_p):
                failed += 1
                print(f"  ✗ kunde inte hämta {it['link']}")
                continue
            info = json.load(open(info_p, encoding="utf-8"))
            meta = " ".join([info.get("description") or "", info.get("title") or "", " ".join(info.get("tags") or [])])
            if not AI_WORDS.search(meta):
                continue
            vtts = sorted(glob.glob(os.path.join(work, "*.vtt")), key=lambda p: (".eng" not in p and ".swe" not in p, p))
            text, how = (vtt_to_text(vtts[0]), "TikTok-undertext") if vtts else ("", "")
            if not text:
                text, how = whisper_text(it["link"], work), "Whisper"
            results.append({
                "saved": it["date"], "link": it["link"], "creator": info.get("uploader") or info.get("channel") or "",
                "caption": (info.get("description") or "").strip(), "how": how, "text": text or "(ingen text)",
            })
            print(f"  ✓ {len(results)}/{want} @{results[-1]['creator']} ({how})")

    with open(os.path.join(outdir, "transkript.md"), "w", encoding="utf-8") as f:
        f.write(f"# Transkript – sparade TikTok-videor om AI\n\n{len(results)} AI-videor (av {checked} genomgångna, "
                f"{failed} gick inte att hämta). Nyast sparade först.\n\n")
        for i, r in enumerate(results, 1):
            f.write(f"## {i}. @{r['creator']} – sparad {r['saved']}\n{r['link']}\nBeskrivning: {r['caption']}\n"
                    f"Källa: {r['how']}\n\nTranskript: {r['text']}\n\n")
    print(f"Klart: {len(results)} transkript i {outdir}/transkript.md")


if __name__ == "__main__":
    main()
