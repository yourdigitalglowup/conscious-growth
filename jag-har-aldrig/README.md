# Jag har aldrig

Festspelet där sanningen kostar fingrar. En enda HTML-fil som fungerar i mobilen, offline och utan inloggning.

## Det här finns i spelet

- **366 påståenden i 11 kortlekar**: Klassiker, Pinsamheter, Svenska synder, Skärmtid, Resor & äventyr, Jobb & plugg, Festminnen, Dejting & kärlek, Pirr, Hemligheter och Vågat 18+ (60 kort).
- **Tre nivåer med ett tryck**: Snällt, Pikant och Vågat. Ni kan också välja kortlekar en och en.
- **Fingerräkning**: lägg in upp till 12 namn. Alla börjar med 3, 5 eller 10 fingrar, och den som är sist kvar vinner.
- **Syndaregister**: ett läge där ingen åker ut och appen bara räknar erkännanden.
- **Twistkort**: *Dubbelt* kostar två fingrar, *Omvänt* betyder att de som INTE har gjort det fäller, och vart tionde kort ungefär är ett regelkort (Pekleken, Ögonkontakt, Tystnad m.fl.). Med Vågat 18+ valt blandas även Heta stolen, Viskleken, Rodnaden, Kyss, gift, dumpa och Raggningsrepliken in.
- **Stegrande hetta**: kvällen börjar med milda kort. Pikanta kort smyger in runt kort 10, och 18+ kommer först runt kort 30, efter ett eget kort som heter ”Dörren stängs”. Går att stänga av under Spelregler.
- **”Bara Sara. Historien, tack!”**: när en enda person har gjort något dyker en lapp upp med en 30-sekundersklocka. Vägrar man berätta kostar det ett finger till (går att ångra).
- **UTE!**: när någon tappar sitt sista finger stämplas det över hela skärmen och telefonen vibrerar. Vinnaren firas med konfetti.
- **Nya kort varje fest**: appen minns vilka kort ni redan har spelat och lägger dem sist i leken. Startknappen visar hur många som är nya.
- **Era egna kort**: internskämt blandas in i leken och sparas till nästa fest.
- **Kvällens utmärkelser**: ställning, Helgonet, Har gjort allt, Ensamvargen och kortet som fällde flest.
- Svep åt vänster för nästa kort och åt höger för att backa. Skärmen hålls tänd under spelet, och spelet sparas om sidan laddas om.

## Spela

Öppna `index.html` i valfri webbläsare. På mobilen kan du välja **Lägg till på hemskärmen**, så startar spelet som en app.

För att få en publik länk: aktivera GitHub Pages för repot (Settings → Pages → Deploy from branch). Då ligger spelet på
`https://<användare>.github.io/conscious-growth/jag-har-aldrig/`.

## Lägga till egna påståenden permanent

Allt innehåll ligger i `DECKS` längst ner i `index.html`. Varje påstående är slutet på meningen ”Jag har aldrig …”, till exempel `'ätit surströmming'`. Lägg till en rad i rätt kortlek. Antalet kort på startsidan räknas automatiskt.

Filen är också uppdelad med kommentarerna `artifact:start` och `artifact:end`. Det som står mellan dem är exakt det som publiceras som Claude-artifact.
