# Vorbild-Analyse: „Bullet Heroes: TD RPG Shooter“

Stand: 28.10.2026

Quellen:
- Google-Play-Eintrag: Beschreibung, 5 Store-Screenshots, Rezensionen
- 8 Screenshots aus dem laufenden Spiel (Gastkonto, Stage 7)

> **Zweck:** Wir bauen ein eigenes Spiel mit ähnlichem Spielgefühl, aber mit eigenem
> Namen, eigenen Figuren, eigener Grafik und eigenen Texten. Diese Datei beschreibt,
> wie das Vorbild funktioniert. Was wir anders machen wollen, steht in Abschnitt 10,
> und was wir nicht übernehmen dürfen, in Abschnitt 12.
>
> Bei Angaben mit „(?)“ ist aus den Bildern nicht sicher erkennbar, wie es funktioniert.

---

## 1. Eckdaten

| | |
|---|---|
| Entwickler | Homa Games (Paris) |
| Paketname | `com.goosebump.bulletheroes` |
| Downloads | über 1 Mio. |
| Bewertung | 4,7 (DE) / 4,4 (US), rund 14.200 Rezensionen |
| Altersfreigabe | USK 12, „Käufe im Spiel (enthält Zufallsartikel)“ |
| Plattformen | Android, Windows (Google Play Games); iOS im Soft Launch |
| Genre | Tower Defense, läuft zum Teil von selbst (Idle), Roguelike-Runs, Helden sammeln |
| Format | Hochformat, eine Hand |
| Stil | Comic-Figuren (Menüs), bunte 3D-Low-Poly-Welt (Kampf, Basislager) |
| Offline | Kämpfe laufen offline; Überfälle im Basislager vermutlich nicht |

---

## 2. Die Kern-Schleife

1. **Hauptmenü:** Stage und Schwierigkeit wählen, „Kampf“ kostet 5 Energie.
2. **Run:** Gegnerwellen laufen von oben auf einen Zaun zu. Die Helden schießen automatisch, die Munition kommt aus einer Schneide-Maschine.
3. **Im Run aufsteigen:** Bei jedem Aufstieg wählt man 1 von 3 Karten: einen neuen Helden aufnehmen oder einen Helden verbessern.
4. **Bosse:** Jedes Gebiet endet mit einem Boss, jede Stage mit einem Endboss.
5. **Belohnung:** Gold, Totenköpfe, Medaillen, Erkennungsmarken und Heldenkarten für mehrere Helden. Eine Siegesserie erhöht die Belohnung.
6. **Außerhalb der Runs aufwerten:**
   - Helden: Level mit Karten, Rang mit Medaillen, Fähigkeiten mit Erkennungsmarken
   - Tech-Baum und Talente (Upgrades)
   - Booster
   - Basislager
7. **Nebenher:**
   - Basislager produziert Münzen und Heldenkarten
   - Überfälle auf andere Basen
   - Tägliche Belohnungen, Glücksrad, Battle Pass

---

## 3. Kampf (ein Run)

### Bildschirm-Aufbau (von oben nach unten)

- **Kopfzeile:**
  - Pause-Knopf
  - „Gebiet 3“ und „Welle 15/15“
  - ein **Erfahrungsbalken** mit grünem Edelstein-Symbol. Besiegte Gegner füllen ihn. Ist er voll, kommt „Fähigkeit wählen“, der Balken beginnt von vorn, und das Ziel wird größer. Beispiel aus einem Run:
    - Welle 1: 0/13
    - Welle 2: 5/13
    - Aufstieg, dann Welle 3: 2/16
    - Welle 4: 12/16
    - Aufstieg, dann 2/20
    - In Welle 15 steht er bei 48/112.
  - „x1 Tempo“ zum Umschalten der Geschwindigkeit
- **Gold im Run** am rechten Rand (z. B. 50), zum Beispiel aus „Kopfgeld“
- **Gegnerfeld:** Ein Pfad, eine Bahn oder eine Brücke, auf der die Gegner von oben nach unten laufen. Jeder hat einen Lebensbalken, Schadenszahlen und Effekte wie „BUMM!“ schweben auf.
  - Bosse tragen eine Krone und haben ein Totenkopf-Symbol mit großem Lebensbalken.
  - Gegnertypen: Skelette, Zombies, Schildkröten, rote Schleimwesen, Roboter, Aliens, Monster. Jede Welt hat ein eigenes Thema, etwa Friedhof, Strand oder Himmelsschloss.
  - Wetter: Regen
- **Zaun** quer über den Bildschirm mit gemeinsamen Lebenspunkten (z. B. 1621/1700). Gegner, die ihn erreichen, greifen ihn an. Heilung zeigt grüne Pluszeichen. Fällt der Zaun, ist der Run verloren (?).
- **Effekte am Zaun:** zum Beispiel eine Feuerwand über die ganze Breite (Boomers Fähigkeit?) und ein Fallschirmspringer-Symbol bei den Gegnern (Luftangriff?)
- **Geschützreihe:** bis zu 3 (?) Helden an festen Plätzen. Je Held:
  - darüber ein Magazin (4 Patronen-Symbole, verbrauchte werden dunkel) und ein Nachladebalken
  - darunter seine Stufe im Run (1, 2, …) mit einem Fortschrittsbogen
- **Unten links:** große **Revolvertrommel**, die „Schneide-Maschine“. Patronen stecken in den Kammern und fliegen von dort zu den Helden.
- **Unten rechts:** **Patronen-Ablage** (Raster mit ca. 10–12 Patronen), der Vorrat
- **Darunter:** Sechseck mit Zahl und 3–4 Segmenten. Die Zahl bleibt im ganzen Run bei 1, die Segmente füllen sich. Vermutlich die Stufe der Trommel (?)
- **Untere Knopfleiste:**
  - links und rechts die **2 aktiven Booster** (z. B. Luftangriff, Hyper-Pill), mit Abklingzeit als Kreisbogen
  - in der Mitte ein großer **Blitz-Knopf**, vermutlich die „Energie-Kugel“ aus dem Tech-Baum. Er **lädt sich im Lauf des Kampfs auf**: Der Kreis füllt sich blau, in Welle 1 zu ¼, in Welle 2 zur Hälfte, in Welle 4 ganz. Dann ist er einsetzbar. Was er auslöst, ist offen.
  - Im Store-Screenshot gibt es noch einen runden Booster-Knopf am rechten Rand (Felsbrocken).

### Munition („Bullet Cutting“)

Das ist das Markenzeichen des Spiels:

- Über der Trommel dreht sich ein Messerarm, auf einem Bild als Kreuz mit mehreren Klingen. Er schneidet aus den Löchern der Trommel Patronen.
- Die Patronen fliegen einzeln zu den Helden und füllen ihr Magazin.
- Die Ablage rechts füllt sich im Lauf des Runs: in Welle 1 mit 5, in Welle 2 mit 7, in Welle 4 mit 10 Patronen. Vermutlich landet dort, was die Helden gerade nicht brauchen (?).
- Ohne Munition schießen die Helden nicht.
- Mehr Löcher bedeuten mehr Patronen pro Umdrehung:
  - im Run die Karte „Schneider-Loch: +1 Loch, mehr Munition erhalten“ (bis 4 Sterne)
  - im Basislager „Loch vergrößern +1“
- Die Store-Beschreibung nennt „Munition“ als eine von drei Upgrade-Säulen (Skills, Feuerkraft, Munition).

**Was der Spieler selbst tut:** Nach den Screenshots läuft der Kampf weitgehend
automatisch. Der Spieler wählt Karten, setzt die Booster und den Blitz-Knopf ein und
schaltet das Tempo um. **Offen:** Kann man auch an der Trommel oder den Patronen etwas
tun, etwa tippen, um schneller zu schneiden? Siehe Abschnitt 11.

### Aufstieg im Run („Fähigkeit wählen“)

- **Zu Beginn: „Held wählen“.** Das Spiel bietet 3 Helden an, jeder mit einem kurzen Satz:
  - Boomer: „Schießt Granaten. Stiftet Chaos“
  - Sparky: „Trifft einen, schockt viele“
  - Frost: „Verursacht Schaden durch breite Salven“

  Die Kartenfarben sind unterschiedlich (grau, orange, blau), vielleicht nach Seltenheit (?). Ob die 3 Helden zufällig angeboten werden, ist offen.
- Beim Aufstieg erscheinen **3 Karten**. Ein kleines Bild über der Karte zeigt, ob sie einen Helden oder die Trommel betrifft. Beispiele:
  - „Held hinzufügen: Tracer, Schnellfeuer-Offizier, +7 Munition erhalten“ (grüne Karte)
  - „Schaden +15 %“
  - „Einfrierchance +5 %“
  - „Schnelles Nachladen: +30 % Nachladegeschwindigkeit“ (höchstens 3 Sterne)
  - „Explosionsradius +20 %“ (höchstens 3 Sterne)
  - „Kritische Chance +10 %“ (höchstens 5 Sterne)
  - „Betäubungsrakete: +10 % Chance auf EMP-Betäubungsraketen“ (höchstens 3 Sterne), mit einem grünen Hinweis „Kette“. Vielleicht gehört die Karte zu einer Kette, die eine stärkere Fähigkeit freischaltet (?).
  - „Schneider-Loch: +1 Loch, mehr Munition erhalten“ (Trommel, höchstens 4 Sterne)
- Jede Verbesserung lässt sich mehrfach nehmen. Die Sterne zeigen die Stufe, wie viele es höchstens gibt, hängt von der Karte ab.
- **„Neu würfeln“:** gegen Werbung 3 neue Karten (1-mal pro Run?)
- **„Alles nehmen“:** gegen Werbung alle 3 Karten auf einmal
- **„Röntgen“** (Auge-Symbol): blendet die Karten aus, um aufs Spielfeld zu schauen (?)
- Der Run pausiert während der Auswahl.
- Laut Rezensionen teilt das Spiel die angebotenen Helden zufällig zu. Tagesmissionen verlangen manchmal bestimmte Helden-Kombinationen.

### Ablauf einer Stage

- Eine Stage (z. B. „7. Himmelsschloss“) hat **7 Gebiete**.
- Die Anzeige „Gebiet 3/7“ zeigt Segmente: geschafft (gelb), aktuell (grün), ein Zwischenboss (Totenkopf) und der Endboss (Totenkopf mit Krone) am Ende.
- Jedes Gebiet hat mehrere Wellen (z. B. 11, 12 oder 15).

### Ende eines Runs („Gewonnen“)

- **Belohnungen**, als Karten nebeneinander:
  - Gold (z. B. 911)
  - Totenköpfe (5, Zweck unklar (?), vielleicht Battle Pass oder Rangliste)
  - Medaillen (2)
  - Erkennungsmarken (27)
  - Heldenkarten für **alle** freigeschalteten Helden, auch für die, die nicht mitgespielt haben (z. B. 6, 1, 7, 8, 8), jeweils mit Fortschrittsbalken. Ein gelber Pfeil zeigt an, dass ein Held aufsteigen kann.
- **Siegesserie** (z. B. 13): Ein Balken von 0 bis MAX. Bei MAX gibt es +10 % Gold. „Gewinne und erhöhe deine Belohnungen“.
- **„2x Belohnungen“** (Gold) gegen Werbung, 3-mal verfügbar; mit SVIP ohne Werbung
- „Zum Fortfahren tippen“

---

## 4. Hauptmenü (Reiter „Kampf“)

- **Kopfzeile** (überall gleich):
  - Profilbild und Name
  - Energie 27/30
  - Gold
  - Diamanten
  - Einstellungen
  - Jede Anzeige hat ein grünes „+“ zum Shop. Das erste Feld wechselt je nach Reiter: Energie, Sterne, Medaillen oder Stadtmünzen.
- **Battle Pass:** Fortschritt 20/50, Stufe 3
- **Schwierigkeit:** Normal / Schwer
- **Stage-Karte** mit Bild der Gegner, Name, Gebietsfortschritt
- **„Kampf“** (kostet 5 Energie) und **„Spielmodus“**. Dort liegen vermutlich Boss Rush und Survival.
- **Linke Leiste:** zeitlich begrenzte Angebote mit Countdown, z. B. Tracer-Paket, Vespera (20 Std.), Mr. Bluff (15 Std.)
- **Rechte Leiste:**
  - „No Ads / SVIP“
  - „Keine Werbung“
  - „Täglich“ (Geschenk mit Countdown)
  - „Ranglisten“
  - „Glücksrad“
- **Untere Leiste (5 Reiter):** Shop · Sammlung · Kampf · Upgrades · Basislager

---

## 5. Sammlung

### Helden

Ein Held wächst auf drei Wegen:

1. **Level** mit **Heldenkarten**, z. B. Level 4 bei 6/20 Karten. Jedes Level erhöht seine Werte.
2. **Rang** mit **Medaillen**: Rekrut (1) → Kadett (2) → … Der erste Aufstieg kostet 5 Medaillen. Jeder Rang bringt eine **Belohnung**, z. B. „Kopfgeld: 15 % der Feinde werfen 10 Gold ab, wenn sie besiegt werden“. In der Sammlung zeigen manche Helden statt Karten einen Medaillen-Balken (17/50). Vermutlich hängt das Level am Rang: Erst nach dem Rang-Aufstieg geht es weiter (?).
3. **Fähigkeiten** mit **Erkennungsmarken**: 4 Plätze pro Held. Sie werden mit dem Level freigeschaltet (z. B. ab Level 7 und ab Level 12) und lassen sich auf je 3 Sterne ausbauen (z. B. für 250 oder 300 Marken).

**Detailansicht eines Helden** (Beispiel Boomer):
- großes Bild und Rang-Abzeichen
- je 2 Fähigkeiten links und rechts
- darunter 3 gesperrte Sechseck-Plätze, vermutlich Ausrüstung oder Rang-Sterne (?)
- Pfeile, um zwischen den Helden zu blättern
- Werte als „jetzt → nach dem nächsten Level“:
  - Schaden 295 → 313
  - Nachladezeit 2,16 → 2,06 s
  - Magazin 1
- Knopf „Rang-Aufstieg“ für 5 Medaillen

Laut einer Rezension endet ein Held bei Level 14.

| Held | Typ (laut Bild/Text) | Freischaltung | Stand im Gastkonto |
|---|---|---|---|
| Tracer | Soldat, Schnellfeuer („Fast Shooting Officer“) | Start-Held | Level 9, Karten 50/200 |
| Frost | „Schaden durch breite Salven“, Einfrieren | früh im Spiel | Level 8, Medaillen 17/50 |
| Nova | Laser. Fähigkeiten: „Hen Grenade“ (Gegner wird zum Huhn), „Lava Pool“, Strahlen (?), Kettenblitz (?) | früh im Spiel | Level 8, Medaillen 17/50 |
| Sparky | Kettenblitz: „Trifft einen, schockt viele“ | Spielfortschritt (?) | Level 7, Karten 56/100 |
| Boomer | „Schießt Granaten. Stiftet Chaos“: Raketen, Explosionen, Feuerwand am Zaun, Betäubungsraketen. Fähigkeiten: Raketen-Explosion, Feuersäule, 2 noch gesperrt. Magazin 1, langsam, viel Schaden | Spielfortschritt (?) | Level 4, Karten 6/20, Rang Rekrut |
| Drako | Drache | Event: 1000 Event-Münzen sammeln (Shop-Reiter „Drako“) | 1/1000 |
| Mr. Bluff | Kartenspieler, Joker | nur über Kaufangebot | gesperrt |
| Brambo | Kämpfer mit Stirnband | nur über Kaufangebot | gesperrt |
| Vespera | Vampirin mit Fledermaus, macht Feinde zu Verbündeten | Kaufpaket 30,99 € (zeitlich begrenzt) | gesperrt |
| Ivy | (?) | Spielfortschritt (ca. Stage 12) | gesperrt |
| Cybo | Roboter | Spielfortschritt (ca. Stage 17) | gesperrt |
| G.O.A.T. (?) | unbekannt, nur als „G.O.A.T.s Clubhaus“ im Basislager gesehen | (?) | – |

### Booster

- **2 aktive Plätze** („Aktive Booster 2/2“). Die Booster werden im Kampf über den runden Knopf eingesetzt (?).
- Bekannte Booster:
  - Luftangriff (Level 1)
  - Hyper-Pill (Level 2)
  - Medipack (Level 2)
  - Panzer (Level 1)
  - Pinguin (Level 1)
  - Felsbrocken (aus dem Store-Screenshot)
- Aufgewertet werden sie mit **Booster-Karten** (z. B. 0/2 oder 0/5).

---

## 6. Upgrades

### Tech-Baum

Eine senkrechte Kette von Knoten, die nacheinander freigeschaltet werden: erledigt (Haken),
aktuell (gelb) oder gesperrt (Schloss). Gesehen:

1. Energie-Kugel verbessern (erledigt, daneben eine Zahl „4“ (?))
2. Zaun: mehr Lebenspunkte (erledigt)
3. Zaun: Heilung bzw. Leben + (aktuell)
4. Trommel verbessern (gesperrt)
5. weitere (gesperrt)

Womit man bezahlt, ist offen, vermutlich mit Gold.

### Talente

- Ein Raster mit mindestens 20 verdeckten Feldern („?“).
- Freigeschaltet sind bisher:
  - Schnelllader (Level 1): schneller nachladen
  - Sanitätskoffer (Level 1): Booster-Karte, Herz und Zaun auf dem Bild, vermutlich heilt der Zaun beim Einsatz eines Boosters (?)
- „Talent erhalten“ zieht ein **zufälliges** Talent:
  - entweder **1 Stern**
  - oder **Werbung ansehen** (3/3, vermutlich pro Tag)

---

## 7. Basislager

Ein zweites Spiel neben den Kämpfen, ähnlich wie „Coin Master“.

**Karte:** Eine isometrische Fläche mit Bauplätzen. Jedes Gebäude gehört zu einem Helden.

| Gebäude | Zustand | Funktion |
|---|---|---|
| Tracers Zelt | gebaut, Level 6 (Aussehen ändert sich bis Level 15) | alle 8 Std. 10 Tracer-Karten (nächste Stufe 11) |
| Novas Kuppel | gebaut | alle 8 Std. Nova-Karten |
| Frosts Iglu | gebaut, Level 5 | alle 8 Std. 8 Frost-Karten (nächste Stufe 10) |
| Sparkys Labor | Bauplatz, 1.500 Stadtmünzen | (Sparky-Karten?) |
| G.O.A.T.s Clubhaus | Bauplatz, 5.000 Stadtmünzen | (?) |
| Boomers Bunker | Bauplatz, 12.000 Stadtmünzen | (Boomer-Karten?) |
| eine Höhle, ein Tresor | Bauplatz (Preis abgeschnitten) | (?) |

**Produktion:**
- **Stadtmünzen-Schneider:** dieselbe Revolvertrommel wie im Kampf. Sie schneidet Stadtmünzen.
  - Level 1 → 2: „Loch vergrößern +1“ für 3.000 Stadtmünzen, also mehr Münzen pro Durchgang.
- **Stadtmünzen-Lager:** die Ablage, die man von Hand leert (18/242, „Sammeln“).
  - Level 2 → 3: Kapazität +54, „kostenlos“ gegen Werbung.
- **„2x für 8 Stunden“:** doppelte Produktion gegen Werbung.
- Bei den Gebäuden heißt der Knopf „Kostenlos“. Vermutlich holt man damit gegen Werbung sofort ab, statt den Timer abzuwarten.

**Angriff und Schutz:**
- **Überfall** (3/3 Versuche): eine fremde Basis angreifen und vermutlich Stadtmünzen erbeuten
- **Rache:** die Person angreifen, die einen selbst überfallen hat
- **Schilde** (1/3, kaufbar): Schutz vor Überfällen
- Ob die Basen echten Spielern gehören oder vom Computer stammen, ist offen. Echte Spieler bräuchten einen Server.

---

## 8. Shop und Geld

- **Reiter:** Angebote · Truhen · Aufladung (Diamanten kaufen) · Drako (Event)
- **SVIP-Karte:** Werbung überspringen und 5 weitere Vorteile (laut Rezension 50 €)
- **„Keine Werbung“:** separater Kauf im Hauptmenü
- **Heldenpakete:** „einmal begrenzt“ mit Countdown, z. B. Vespera + 750 Diamanten + 5 Schlüssel für 30,99 €
- **Sonderangebote nach Level:** z. B. „Level-6-Geschenkpaket“ für 19,99 € mit 300 Diamanten, 15.000 Gold, 5 goldenen Schlüsseln, 5 Schraubenschlüsseln und Heldenkarten, beworben mit „Bonus 200 %“
- **Truhen** mit Zufallsinhalt (darauf bezieht sich die USK-Angabe „Zufallsartikel“), geöffnet mit Schlüsseln
- **Battle Pass**, **Glücksrad**, **Tägliche Belohnung**
- **Werbung:**
  - Pflichtwerbung nach jedem Level und mehrmals im Level (laut Rezensionen)
  - freiwillig für: Upgrade kostenlos, Talent ziehen, sofort abholen, 2x Produktion, doppelte Belohnung nach dem Sieg (3-mal), „Alles nehmen“ und „Neu würfeln“ bei der Kartenauswahl
- **2x Kampftempo** kostet laut Rezension rund 15 €.

---

## 9. Währungen und Ressourcen

| Ressource | Wofür | Woher |
|---|---|---|
| Energie (max. 30) | einen Kampf starten (5 pro Kampf) | lädt mit der Zeit auf, kaufbar |
| Gold | Aufwerten (Tech-Baum? Helden?) | Kämpfe, Kopfgeld, Pakete |
| Diamanten | Premium-Währung | Kauf, Pakete, Belohnungen |
| Heldenkarten (je Held) | Helden-Level | Kämpfe (für alle Helden), Basislager-Gebäude, Truhen |
| Medaillen | Rang-Aufstieg eines Helden | Kämpfe |
| Erkennungsmarken | Fähigkeiten der Helden ausbauen | Kämpfe |
| Totenköpfe | (?) | Kämpfe |
| Booster-Karten | Booster aufwerten | (?) |
| Sterne | Talente ziehen (1 Stern = 1 Talent) | (?) vermutlich Stage-Abschluss |
| Stadtmünzen | Basislager ausbauen | Stadtmünzen-Schneider, Überfälle |
| Schlüssel (Silber, Gold) | Truhen öffnen | Pakete, (?) |
| Schraubenschlüssel | (?) | Pakete |
| Event-Münzen | Event-Held (Drako, 1000 Stück) | Event |
| Schilde (max. 3) | Schutz vor Überfällen | (?), kaufbar |
| Battle-Pass-Punkte | Battle-Pass-Stufen | (?) |

Das sind **rund 15 Ressourcen**. Für ein Hobby- bzw. Erstprojekt sind das deutlich zu viele, siehe Abschnitt 10.

---

## 10. Was Spieler kritisieren und was wir anders machen können

| Kritik am Vorbild (Rezensionen) | Idee für unser Spiel |
|---|---|
| Pflichtwerbung nach jedem Level und im Level („6 von 10 Minuten Werbung“) | Werbung nur freiwillig gegen Belohnung, nie erzwungen; dazu ein fairer Einmalkauf „ohne Werbung“ |
| 2x-Tempo kostet ca. 15 € | 2x-Tempo kostenlos, ab einer frühen Stage |
| Neue Helden nur gegen viel Geld oder nach Jahren erreichbar | Jeder Held ist durch Spielen in absehbarer Zeit erreichbar |
| Helden enden bei Level 14, danach „öde“ | Kein hartes Ende: ein endloser Modus mit Ranglisten, ein Neustart mit Bonus (Prestige) oder saisonale Welten |
| Tagesmission mit Helden-Kombination ist unlösbar | Missionen nur mit Zielen, die immer lösbar sind |
| Gold „verschwindet“, Fehler bei Belohnungen | Spielstand sauber speichern und testen |
| Sehr viele Währungen, Kaufdruck | Wenige Ressourcen, z. B. Münzen, Heldenkarten, Edelsteine |

**Was gut ankommt und bleiben sollte:**
- kurze Runs für zwischendurch
- das befriedigende Gefühl der Munitions-Maschine
- Helden sammeln und kombinieren
- die Kartenauswahl im Run
- Bosse
- Offline spielbar

**Technischer Hinweis:** Überfälle auf echte Spieler brauchen einen Server, und ein Server kostet Geld.
Vorschlag: erst ohne Überfälle starten oder mit Computer-Basen, die gar keinen Server brauchen.

---

## 11. Noch offen (diese Screenshots fehlen noch)

1. **Kampf:**
   - Was löst der große Blitz-Knopf aus, wenn er voll ist?
   - Kann man an der Trommel oder den Patronen selbst etwas tun, etwa tippen?
   - Werden die 3 Start-Helden zufällig angeboten?
   - Was bedeutet der Hinweis „Kette“ auf einer Karte?
2. **„Spielmodus“:** Boss Rush und Survival
3. **Niederlage:** Was passiert, wenn der Zaun fällt? Gibt es eine zweite Chance gegen Werbung?
4. **Helden:**
   - Wie viele Ränge gibt es?
   - Was sind die 3 Sechseck-Plätze?
   - Wie hängen Level und Rang zusammen?
5. **Überfall:** wie er abläuft
6. Battle Pass, Glücksrad, Truhen, Tagesmissionen, Ranglisten; wofür die Totenköpfe sind
7. Einstellungen (Ton, Vibration)

---

## 12. Was wir nicht übernehmen dürfen

Spielideen und Spielabläufe (Genre, Kern-Schleife, Kartenauswahl, Basisbau) darf man
nachbauen. **Nicht übernehmen dürfen wir:**

- den Namen „Bullet Heroes“ und ähnlich klingende Namen
- das Logo, auch nicht das „O“ als Revolvertrommel
- Figuren und ihre Namen (Tracer, Frost, Nova, Vespera …) samt Aussehen
- Grafiken, Icons, Hintergründe, Animationen
- Texte, Sounds, Musik
- den Code bzw. Teile der App

Die Grafiken auf den Screenshots gehören Homa Games. Deshalb liegen die Screenshots
**nicht** in diesem Repository. Hier steht nur die Beschreibung.

*(Keine Rechtsberatung. Vor einer Veröffentlichung gesondert prüfen.)*
