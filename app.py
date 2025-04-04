import streamlit as st
import datetime
import os
import json
import pandas as pd
import plotly.express as px
import random

# OBS: st.set_page_config måste vara det FÖRSTA Streamlit-kommandot i din app
st.set_page_config(
    page_title="Lindas Conscious Growth AI",
    page_icon="💖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Lägg till anpassad CSS för att göra appen vackrare
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #FF69B4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #8A2BE2;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .highlight-box {
        background-color: #F0F8FF;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1E90FF;
        margin-bottom: 1rem;
    }
    .action-box {
        background-color: #E6F9E6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #32CD32;
        margin-bottom: 1rem;
    }
    .pep-box {
        background-color: #FFE6F9;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FF69B4;
        margin-bottom: 1rem;
    }
    .question-box {
        background-color: #FFF4E1;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #FFA500;
        margin-bottom: 1rem;
    }
    .celebration-box {
        background-color: #FFFACD;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px dashed #FFD700;
        margin: 1.5rem 0;
        text-align: center;
    }
    .emoji-large {
        font-size: 2rem;
    }
    .streak-container {
        display: flex;
        justify-content: space-between;
        margin: 1rem 0;
    }
    .streak-box {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        width: 30%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .streak-label {
        font-size: 0.9rem;
        color: #6C757D;
    }
    .streak-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #007BFF;
    }
</style>
""", unsafe_allow_html=True)

# Funktioner för datahantering
def get_streak_data():
    """Hämtar information om inchecknings-streak"""
    # I Streamlit använder vi sessions state för att spara data mellan körningar
    if 'streak_data' not in st.session_state:
        # Första gången eller om filen inte finns
        streak_file = "lindas_streak_data.json"
        if os.path.exists(streak_file):
            with open(streak_file, "r", encoding="utf-8") as f:
                st.session_state.streak_data = json.load(f)
        else:
            st.session_state.streak_data = {
                "current_streak": 0,
                "last_check_in": "",
                "highest_streak": 0,
                "total_check_ins": 0,
                "feelings_log": [],  # Lista för att spåra känslor över tid
                "phases_log": []     # Lista för att spåra energifaser över tid
            }
    
    return st.session_state.streak_data

def update_streak(feeling, energy_phase):
    """Uppdaterar inchecknings-streak och returnerar streak-data"""
    streak_data = get_streak_data()
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    
    # Spara känsla och fas för trendanalys
    if 'feelings_log' not in streak_data:
        streak_data['feelings_log'] = []
    if 'phases_log' not in streak_data:
        streak_data['phases_log'] = []
    
    # Lägg till dagens data i loggen
    streak_data['feelings_log'].append({"date": today, "feeling": feeling})
    streak_data['phases_log'].append({"date": today, "phase": energy_phase})
    
    # Uppdatera total antal incheckningar
    streak_data["total_check_ins"] += 1
    
    # Om detta är första incheckningen eller om sista incheckningen var igår
    if streak_data["last_check_in"] == "" or streak_data["last_check_in"] == yesterday:
        streak_data["current_streak"] += 1
    # Om sista incheckningen var idag, ändra ingenting
    elif streak_data["last_check_in"] == today:
        pass
    # Annars, återställ streak till 1
    else:
        streak_data["current_streak"] = 1
    
    # Uppdatera högsta streak om aktuell streak är högre
    if streak_data["current_streak"] > streak_data["highest_streak"]:
        streak_data["highest_streak"] = streak_data["current_streak"]
    
    # Uppdatera datum för senaste incheckning
    streak_data["last_check_in"] = today
    
    # Spara uppdaterad data
    with open("lindas_streak_data.json", "w", encoding="utf-8") as f:
        json.dump(streak_data, f, indent=2)
    
    st.session_state.streak_data = streak_data
    return streak_data

def get_celebration_message(streak):
    """Returnerar ett firande meddelande baserat på streak-längd"""
    
    # Milestone achievements och belöningar
    celebrations = {
        3: {
            "message": "🎉 Fantastiskt, Linda! Du har checkat in 3 dagar i rad! Du bygger en kraftfull vana.",
            "affirmation": "Jag växer starkare för varje dag och varje litet steg jag tar.",
            "challenge": "Utmaning: Skriv ner en sak du är extra stolt över med dig själv idag!"
        },
        5: {
            "message": "🎉 WOW Linda! 5 dagars streak! Du är en inspirerande kraft av fokus och dedikation.",
            "affirmation": "Min uthållighet är min superkraft. När jag fortsätter, skapar jag magi.",
            "challenge": "Utmaning: Skriv ner tre saker du är extra stolt över med dig själv den senaste veckan!"
        },
        7: {
            "message": "🎉 OTROLIGT Linda! En hel veckas incheckning i rad! Du är en stjärna av konsistens!",
            "affirmation": "Jag är disciplinerad, jag är medveten, jag är i kontakt med min inre kraft varje dag.",
            "challenge": "Utmaning: Avsluta meningen 'Om jag fortsätter på denna väg, kommer jag om ett år att...'"
        },
        10: {
            "message": "🎉 MÄKTIGT Linda! 10 dagars streak - detta är en STOR milstolpe! Du är en naturkraft!",
            "affirmation": "Jag förvandlar små dagliga handlingar till livslånga underverk. Jag är stolt över min resa.",
            "challenge": "Utmaning: Ta en stund att blunda och visualisera hur du firar dig själv om 30 dagar. Vad ser du?"
        },
        14: {
            "message": "🎉 MAKALÖST Linda! TVÅ HELA VECKOR! Du är en legend av personlig utveckling!",
            "affirmation": "Varje dag blir jag mer av den jag är menad att vara. Min potential är oändlig.",
            "challenge": "Utmaning: Skriv ett kort kärleksbrev till dig själv - från ditt framtida jag om ett år."
        },
        21: {
            "message": "🎉 ÖVERJORDISKT Linda! 21 dagar - du har skapat en djup vana som förändrar din hjärna!",
            "affirmation": "Jag är skaparen av min verklighet. Varje dag bygger jag den med medvetenhet och kärlek.",
            "challenge": "Utmaning: Välj ett område i ditt liv du vill se blomstra - skriv 3 specifika sätt du redan ser små framsteg där."
        },
        30: {
            "message": "🎉 VÄRLDSKLASS Linda! EN HEL MÅNAD! Du är i en elitgrupp av medvetna själsutvecklare!",
            "affirmation": "Jag följer mitt hjärtas kompass. Min uthållighet är mitt vittne om min inre visdom.",
            "challenge": "Utmaning: Reflektera och skriv ner: Vilka 3 små förändringar har du märkt i ditt liv sedan du började denna resa?"
        }
    }
    
    # Hitta den högsta uppnådda milstolpen
    achieved_milestone = 0
    for milestone in sorted(celebrations.keys()):
        if streak >= milestone:
            achieved_milestone = milestone
        else:
            break
    
    # Returnera firande om en milstolpe är uppnådd
    if achieved_milestone > 0:
        return celebrations[achieved_milestone]
    
    # Inget firande om ingen milstolpe är uppnådd
    return None

def generate_microaction(feeling, energy_phase):
    """Genererar en mikroaction baserat på känslor och energifas"""
    
    # Kombinationer av känslor och energifaser
    actions = {
        ("Energisk", "Bygga"): "Ta 15 minuter för att skapa en visuell plan för ett projekt du vill slutföra.",
        ("Energisk", "Skapa"): "Dedikera 20 minuter till att arbeta på ett kreativt projekt som ger dig glädje.",
        ("Energisk", "Fördjupa"): "Läs 10 sidor i en bok som utvecklar dina kunskaper inom ett område du brinner för.",
        ("Energisk", "Vila"): "Ta en promenad utomhus i 15 minuter för att omvandla din energi till positiv återhämtning.",
        
        ("Trött", "Bygga"): "Gör en enkel att-göra-lista med max 3 små uppgifter som känns hanterbara idag.",
        ("Trött", "Skapa"): "Skapa något litet och enkelt idag, kanske en kort dikt eller en snabb skiss.",
        ("Trött", "Fördjupa"): "Lyssna på en inspirerande podcast i 10 minuter.",
        ("Trött", "Vila"): "Ta en power-nap på 20 minuter eller meditationspaus.",
        
        ("Stressad", "Bygga"): "Bryt ner en stressande uppgift i 3 små, hanterbara steg och fokusera bara på det första.",
        ("Stressad", "Skapa"): "Ägna 10 minuter åt en kreativ aktivitet som hjälper dig slappna av, som att rita eller färglägga.",
        ("Stressad", "Fördjupa"): "Skriv ner 3 saker du är tacksam över för att få perspektiv.",
        ("Stressad", "Vila"): "Gör 5 minuter djupandning eller en kort guidad avslappningsövning.",
        
        ("Inspirerad", "Bygga"): "Skissa på en plan för hur du kan förverkliga en idé som inspirerar dig.",
        ("Inspirerad", "Skapa"): "Fånga din inspiration genom att skriva eller skissa i 15 minuter utan att censurera dig själv.",
        ("Inspirerad", "Fördjupa"): "Dela din inspiration med någon som kan hjälpa dig utveckla idén vidare.",
        ("Inspirerad", "Vila"): "Visualisera din inspirerande idé i 10 minuter medan du slappnar av.",
        
        ("Lugn", "Bygga"): "Använd din lugna energi till att planera eller organisera något du skjutit upp.",
        ("Lugn", "Skapa"): "Skapa något som lugnar dig ytterligare, som en vacker lista eller en inspirerande tavla.",
        ("Lugn", "Fördjupa"): "Fördjupa din lugna känsla genom att läsa något reflekterande i 15 minuter.",
        ("Lugn", "Vila"): "Njut av ett avslappnande te eller annan dryck medan du bara är närvarande i stunden."
    }
    
    return actions.get((feeling, energy_phase), "Ta 5 minuter för att bara andas djupt och tänka på något som ger dig glädje.")

def generate_pep_talk(feeling, energy_phase):
    """Genererar en peppande reflektion baserat på känslor och energifas"""
    
    # Reflektioner baserade på känslor och energifaser
    reflections = {
        ("Energisk", "Bygga"): "Din energi är en fantastisk gåva idag! När du bygger med sådan kraft skapar du möjligheter för framtiden.",
        ("Energisk", "Skapa"): "Det lyser kreativitet om dig idag! Din energi och skaparkraft kan flytta berg - njut av flödet.",
        ("Energisk", "Fördjupa"): "Din nyfikenhet och energi är den perfekta kombinationen för djupare förståelse. Låt dig uppslukas av lärandet!",
        ("Energisk", "Vila"): "Även en energisk kropp behöver balans. Din vila idag laddar om batterierna för morgondagens äventyr.",
        
        ("Trött", "Bygga"): "Även när du känner dig trött finns det visdom i att ta små steg framåt. Varje litet framsteg räknas!",
        ("Trött", "Skapa"): "Ibland föds de mest intressanta idéerna när vi inte pressar oss. Låt skapandet vara enkelt och kravlöst idag.",
        ("Trött", "Fördjupa"): "Tröttheten du känner kan vara en signal att sakta ner och verkligen absorbera kunskap på ett djupare plan.",
        ("Trött", "Vila"): "Att lyssna på kroppens signaler är en styrka, inte en svaghet. Din vila idag är en investering i morgondagen.",
        
        ("Stressad", "Bygga"): "Bakom stressen finns en möjlighet att bygga något stabilt och hållbart. Ett litet steg i taget.",
        ("Stressad", "Skapa"): "Kreativitet kan vara en fantastisk ventil för stress. Låt pennan eller penseln förvandla oron till något vackert.",
        ("Stressad", "Fördjupa"): "Att fördjupa sig i något meningsfullt kan hjälpa dig att hitta ett lugn mitt i stormen.",
        ("Stressad", "Vila"): "Din kropp berättar något viktigt. Att vila är inte bara tillåtet, det är nödvändigt för att återställa balansen.",
        
        ("Inspirerad", "Bygga"): "Vilken underbar känsla att vara inspirerad och redo att bygga! Dina idéer är värdefulla och förtjänar utrymme.",
        ("Inspirerad", "Skapa"): "När inspiration och kreativitet möts sker magi. Dina skapelser har förmågan att beröra både dig och andra.",
        ("Inspirerad", "Fördjupa"): "Din inspiration blir ännu mer kraftfull när du fördjupar dig. Kunskapen du söker har väntat på dig.",
        ("Inspirerad", "Vila"): "Låt inspirationen sjunka in medan du vilar. Som ett frö som gror i det tysta kommer den att växa sig starkare.",
        
        ("Lugn", "Bygga"): "Ditt lugn ger dig en stabil grund att bygga från. Som ett ankare i havet står du stadigt i din skapandeprocess.",
        ("Lugn", "Skapa"): "Ditt lugna sinne är den perfekta platsen för att skapa med intention och närvaro. Njut av processen.",
        ("Lugn", "Fördjupa"): "Den lugna energin är perfekt för fördjupning och insikt. Du har förmågan att se bortom ytan.",
        ("Lugn", "Vila"): "Att vara lugn och vila är som att sjunka in i en varm omfamning. Du förtjänar denna stund av total acceptans."
    }
    
    return reflections.get((feeling, energy_phase), "Kom ihåg att varje dag är en ny möjlighet. Du gör ditt bästa, och det är alltid tillräckligt.")

def generate_cycle_question(energy_phase):
    """Genererar en reflektionsfråga baserad på energifas"""
    
    # Cykelfrågor för olika energifaser
    cycle_questions = {
        "Bygga": "Vilket litet steg kan du ta idag som gör att du känner dig starkare och mer grundad?",
        "Skapa": "Vad längtar du efter att uttrycka eller skapa idag, utan att döma det?",
        "Fördjupa": "Vilket område vill du förstå djupare eller utforska lite mer idag?",
        "Vila": "Hur kan du ge dig själv tillåtelse att vila fullt ut idag?"
    }
    
    return cycle_questions.get(energy_phase, "Vad behöver du mest just idag för att känna dig hel och i balans?")

def save_log(feeling, energy_phase, microaction, pep_talk, cycle_question, cycle_reflection=None):
    """Sparar dagens session i en textfil"""
    today = datetime.date.today()
    
    # Se till att filen existerar
    if not os.path.exists("lindas_livspuls_logg.txt"):
        with open("lindas_livspuls_logg.txt", "w", encoding="utf-8") as f:
            f.write("LINDAS LIVSPULS LOGG\n")
            f.write("====================\n\n")
    
    with open("lindas_livspuls_logg.txt", "a", encoding="utf-8") as f:
        f.write("--------------------------------------------------\n")
        f.write(f"Datum: {today}\n")
        f.write(f"Känsla: {feeling}\n")
        f.write(f"Energifas: {energy_phase}\n")
        f.write(f"Mikroaction: {microaction}\n")
        f.write(f"Reflektion (Pep Talk): {pep_talk}\n")
        f.write(f"Cykelreflektionsfråga: {cycle_question}\n")
        if cycle_reflection:
            f.write(f"Lindas reflektion: {cycle_reflection}\n")
        f.write("--------------------------------------------------\n")

def show_trend_analysis():
    """Visar enkel trendanalys baserat på insamlad data"""
    streak_data = get_streak_data()
    
    if 'feelings_log' not in streak_data or len(streak_data['feelings_log']) < 2:
        st.info("Du behöver minst två incheckningar för att se trendanalyser. Kom tillbaka efter att du checkat in några dagar till! 💖")
        return
    
    st.markdown('<div class="sub-header">Din Livspuls över tid</div>', unsafe_allow_html=True)
    
    # Skapa dataframe för känslor
    feelings_df = pd.DataFrame(streak_data['feelings_log'])
    feelings_df['date'] = pd.to_datetime(feelings_df['date'])
    
    # Skapa dataframe för faser
    phases_df = pd.DataFrame(streak_data['phases_log'])
    phases_df['date'] = pd.to_datetime(phases_df['date'])
    
    # Visa grafer
    
    # Känslornas fördelning
    feeling_counts = feelings_df['feeling'].value_counts().reset_index()
    feeling_counts.columns = ['Känsla', 'Antal dagar']
    
    fig1 = px.pie(feeling_counts, values='Antal dagar', names='Känsla', 
                 title='Fördelning av dina känslor över tid',
                 color_discrete_sequence=px.colors.qualitative.Pastel1)
    st.plotly_chart(fig1)
    
    # Energifasernas fördelning
    phase_counts = phases_df['phase'].value_counts().reset_index()
    phase_counts.columns = ['Energifas', 'Antal dagar']
    
    fig2 = px.pie(phase_counts, values='Antal dagar', names='Energifas', 
                 title='Fördelning av dina energifaser över tid',
                 color_discrete_sequence=px.colors.qualitative.Pastel2)
    st.plotly_chart(fig2)
    
    # Känslor över tid
    feelings_time = feelings_df.copy()
    fig3 = px.line(feelings_time, x='date', y='feeling', 
                  title='Dina känslor över tid',
                  labels={'date': 'Datum', 'feeling': 'Känsla'},
                  markers=True)
    st.plotly_chart(fig3)
    
    # Mest vanliga kombinationer
    st.markdown("#### Dina vanligaste känsla-fas kombinationer:")
    
    # Kombinera data
    combined_df = pd.merge(feelings_df, phases_df, on='date')
    combined_df['combo'] = combined_df['feeling'] + ' + ' + combined_df['phase']
    combo_counts = combined_df['combo'].value_counts()
    
    # Visa topp 3 kombinationer
    for i, (combo, count) in enumerate(combo_counts.items()[:3]):
        st.markdown(f"**{i+1}.** {combo}: {count} dagar")
    
    # Insikter baserat på data
    st.markdown("#### Personliga insikter:")
    
    # Vanligaste känslan
    top_feeling = feeling_counts.iloc[0]['Känsla']
    st.markdown(f"🔍 Din vanligaste känsla är **{top_feeling}**")
    
    # Vanligaste energifasen
    top_phase = phase_counts.iloc[0]['Energifas']
    st.markdown(f"🔍 Din vanligaste energifas är **{top_phase}**")
    
    # Något mer personligt...
    insikter = [
        "Du verkar ha bra balans mellan aktivitet och vila",
        f"Du har checkat in {streak_data['total_check_ins']} gånger - varje incheckning bygger din medvetenhet",
        "Ditt engagemang för personlig utveckling är inspirerande",
        "Din konsistens visar på din inre motivation och beslutsamhet",
        f"När du känner dig {top_feeling}, verkar du ofta välja att vara i en {top_phase}-fas"
    ]
    
    st.markdown(f"🔍 {random.choice(insikter)}")

# Huvudfunktion för Streamlit-appen
def main():
    # Visa header
    st.markdown('<div class="main-header">💖 Lindas Conscious Growth AI 💖</div>', unsafe_allow_html=True)
    
    # Hämta streak-data för att visa
    streak_data = get_streak_data()
    current_streak = streak_data.get("current_streak", 0)
    highest_streak = streak_data.get("highest_streak", 0)
    total_checkins = streak_data.get("total_check_ins", 0)
    
    # Visa streak-stats
    st.markdown("""
    <div class="streak-container">
        <div class="streak-box">
            <div class="streak-label">Nuvarande streak</div>
            <div class="streak-value">{} 🔥</div>
        </div>
        <div class="streak-box">
            <div class="streak-label">Högsta streak</div>
            <div class="streak-value">{} 🏆</div>
        </div>
        <div class="streak-box">
            <div class="streak-label">Totalt antal incheckningar</div>
            <div class="streak-value">{} ✅</div>
        </div>
    </div>
    """.format(current_streak, highest_streak, total_checkins), unsafe_allow_html=True)
    
    # Skapa flikar för appens olika delar
    tab1, tab2, tab3 = st.tabs(["Dagens Incheckning", "Trendanalys", "Om Appen"])
    
    with tab1:
        # Startbild och välkomstext
        if "incheckning_klar" not in st.session_state:
            st.session_state.incheckning_klar = False
            
        if not st.session_state.incheckning_klar:
            st.markdown('<div class="sub-header">Välkommen till din dagliga incheckning!</div>', unsafe_allow_html=True)
            
            # Definera känslor och energifaser
            feelings = ["Energisk", "Trött", "Stressad", "Inspirerad", "Lugn"]
            energy_phases = ["Bygga", "Skapa", "Fördjupa", "Vila"]
            
            # Första steget - välj känsla
            st.markdown("### Hur känner du dig idag?")
            feeling = st.radio("", feelings, horizontal=True)
            
            st.markdown("### Vilken energifas känns mest rätt idag?")
            energy_phase = st.radio("", energy_phases, horizontal=True)
            
            # Knapp för att fortsätta
            if st.button("💫 Fortsätt", use_container_width=True):
                # Generera mikroaction, pep talk och cykelfråga
                microaction = generate_microaction(feeling, energy_phase)
                pep_talk = generate_pep_talk(feeling, energy_phase)
                cycle_question = generate_cycle_question(energy_phase)
                
                # Spara i session state för att visa på nästa skärm
                st.session_state.feeling = feeling
                st.session_state.energy_phase = energy_phase
                st.session_state.microaction = microaction
                st.session_state.pep_talk = pep_talk
                st.session_state.cycle_question = cycle_question
                
                # Uppdatera streak och få data
                streak_data = update_streak(feeling, energy_phase)
                current_streak = streak_data["current_streak"]
                
                # Kolla om det finns en celebration för denna streak
                celebration = get_celebration_message(current_streak)
                st.session_state.celebration = celebration
                
                # Ändra tillstånd för att visa resultat
                st.session_state.incheckning_klar = True
                
                # Ladda om sidan för att visa resultat
                st.rerun()
                
        else:
            # Visa resultatet av incheckningen
            st.markdown(f'<div class="highlight-box emoji-large">🌟 Du känner dig {st.session_state.feeling} och är i en {st.session_state.energy_phase}-fas idag 🌟</div>', unsafe_allow_html=True)
            
            # Visa mikroaction
            st.markdown('<div class="action-box">', unsafe_allow_html=True)
            st.markdown("#### ✨ Föreslagen mikroaction för dig idag:")
            st.markdown(f"##### {st.session_state.microaction}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Visa peppande reflektion
            st.markdown('<div class="pep-box">', unsafe_allow_html=True)
            st.markdown("#### 💭 En liten reflektion till dig:")
            st.markdown(f"##### {st.session_state.pep_talk}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Visa reflektionsfråga
            st.markdown('<div class="question-box">', unsafe_allow_html=True)
            st.markdown("#### 💡 Reflektionsfråga för dig idag:")
            st.markdown(f"##### {st.session_state.cycle_question}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Fråga om reflektion
            want_to_reflect = st.radio("Vill du svara på reflektionsfrågan?", ["Ja", "Nej"])
            
            if want_to_reflect == "Ja":
                cycle_reflection = st.text_area("Skriv din reflektion här:")
                if st.button("Spara min reflektion", use_container_width=True):
                    # Spara i loggfilen
                    save_log(st.session_state.feeling, st.session_state.energy_phase, 
                             st.session_state.microaction, st.session_state.pep_talk, 
                             st.session_state.cycle_question, cycle_reflection)
                    
                    st.success("✨ Tack för din vackra reflektion, Linda! Den är nu sparad i din livspuls-logg. ✨")
            else:
                # Spara utan reflektion
                if st.button("Fortsätt utan reflektion", use_container_width=True):
                    save_log(st.session_state.feeling, st.session_state.energy_phase, 
                            st.session_state.microaction, st.session_state.pep_talk, 
                            st.session_state.cycle_question)
                    
                    st.success("📖 Din incheckning har sparats!")
            
            # Visa firande om det finns
            if hasattr(st.session_state, 'celebration') and st.session_state.celebration:
                st.markdown('<div class="celebration-box">', unsafe_allow_html=True)
                st.markdown(f"### {st.session_state.celebration['message']}")
                st.markdown("#### ✨ Dagens affirmation för dig:")
                st.markdown(f"*{st.session_state.celebration['affirmation']}*")
                st.markdown(f"#### {st.session_state.celebration['challenge']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Knapp för att starta en ny incheckning
            if st.button("Starta en ny incheckning", use_container_width=True):
                # Återställ tillstånd
                st.session_state.incheckning_klar = False
                st.rerun()
