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
5. **Belohnung:** Gold, Heldenkarten, Sterne, Battle-Pass-Fortschritt (?).
6. **Außerhalb der Runs aufwerten:**
   - Helden-Level (Sammlung)
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

- **Kopfzeile:** „Area 5“, Fortschrittsbalken mit Edelstein-Symbol (z. B. 51/74, vermutlich besiegte von allen Gegnern), „Wave 11/11“
- **Gegnerfeld:** Ein Pfad bzw. eine Bahn, Gegner laufen von oben nach unten. Jeder hat einen Lebensbalken, Schadenszahlen schweben auf.
  - Bosse tragen eine Krone und haben ein Totenkopf-Symbol mit großem Lebensbalken.
  - Gegnertypen: Skelette, Zombies, rote Schleimwesen, Roboter, Aliens, Monster. Eine Welt hat ein eigenes Thema, etwa Friedhof oder Strand.
  - Wetter: Regen
- **Rechter Rand:** runder Knopf für einen **Booster** (z. B. ein Felsbrocken, der durch die Gegner rollt)
- **Zaun** quer über den Bildschirm mit gemeinsamen Lebenspunkten (z. B. 639/900). Fällt er, ist der Run verloren (?).
- **Geschützreihe:** bis zu 3 (?) Helden an festen Plätzen. Je Held:
  - darüber ein Magazin (4 Patronen-Symbole) und ein Nachladebalken
  - darunter seine Stufe im Run (1, 2, …) mit einem Fortschrittsbogen
- **Unten links:** große **Revolvertrommel**, die „Schneide-Maschine“. Sie stanzt Patronen aus, die zu den Helden fliegen.
- **Unten rechts:** **Patronen-Ablage** (Raster mit ca. 12 Patronen), der Vorrat
- **Ganz unten:** eine Stufen-Anzeige (Sechseck mit Zahl und 4 Segmenten), vermutlich die Stufe der Trommel bzw. Munition im Run (?)

### Munition („Bullet Cutting“)

Das ist das Markenzeichen des Spiels. Die Trommel schneidet bzw. stanzt Patronen. Sie
landen in der Ablage und werden von dort an die Helden verteilt. Ohne Munition schießen
die Helden nicht. Die Store-Beschreibung nennt „Munition“ als eine von drei
Upgrade-Säulen (Skills, Feuerkraft, Munition).

**Offen:** Tippt oder wischt der Spieler dabei selbst, oder läuft alles automatisch? Mehr dazu in Abschnitt 11.

### Aufstieg im Run (Roguelike-Karten)

- Ein Run startet mit **einem Helden**.
- Beim Aufstieg erscheinen **3 Karten**. Ein kleines Heldenbild über der Karte zeigt, welchen Helden sie betrifft. Beispiele:
  - „Damage Boost: Schaden +15 %“
  - „Freeze Chance +5 %“ mit Sternen für die Ausbaustufe (bis 3 Sterne?)
  - „Add Hero: Tracer, Fast Shooting Officer, +7 Munition“
- Laut Rezensionen teilt das Spiel die angebotenen Helden zufällig zu. Tagesmissionen verlangen manchmal bestimmte Helden-Kombinationen.

### Ablauf einer Stage

- Eine Stage (z. B. „7. Himmelsschloss“) hat **7 Gebiete**.
- Die Anzeige „Gebiet 3/7“ zeigt Segmente: geschafft (gelb), aktuell (grün), ein Zwischenboss (Totenkopf) und der Endboss (Totenkopf mit Krone) am Ende.
- Jedes Gebiet hat mehrere Wellen (z. B. 11 oder 12).

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

Jeder Held wird mit **Heldenkarten** aufgewertet, manche Helden mit **Medaillen**.
Warum der Unterschied, ist offen: vielleicht ab einer bestimmten Stufe, vielleicht je nach Seltenheit.
In der Detailansicht hat jeder Held **4 Fähigkeiten**, die mit seiner Stufe nach und nach freigeschaltet werden.
Laut einer Rezension endet ein Held bei Level 14.

| Held | Typ (laut Bild/Text) | Freischaltung | Stand im Gastkonto |
|---|---|---|---|
| Tracer | Soldat, Schnellfeuer („Fast Shooting Officer“) | Start-Held | Level 9, Karten 50/200 |
| Frost | Scharfschütze, Einfrieren | früh im Spiel | Level 8, Medaillen 17/50 |
| Nova | Laser. Fähigkeiten: „Hen Grenade“ (Gegner wird zum Huhn), „Lava Pool“, Strahlen (?), Kettenblitz (?) | früh im Spiel | Level 8, Medaillen 17/50 |
| Sparky | Blitz, Kanone | Spielfortschritt (?) | Level 7, Karten 56/100 |
| Boomer | Bazooka bzw. Raketen | Spielfortschritt (?) | Level 3, Karten 8/10 |
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
  - freiwillig für: Upgrade kostenlos, Talent ziehen, sofort abholen, 2x Produktion
- **2x Kampftempo** kostet laut Rezension rund 15 €.

---

## 9. Währungen und Ressourcen

| Ressource | Wofür | Woher |
|---|---|---|
| Energie (max. 30) | einen Kampf starten (5 pro Kampf) | lädt mit der Zeit auf, kaufbar |
| Gold | Aufwerten (Tech-Baum? Helden?) | Kämpfe, Pakete |
| Diamanten | Premium-Währung | Kauf, Pakete, Belohnungen |
| Heldenkarten (je Held) | Helden aufwerten | Basislager-Gebäude, Truhen, Kämpfe (?) |
| Medaillen | Helden aufwerten (höhere Stufen oder bestimmte Helden?) | (?) |
| Booster-Karten | Booster aufwerten | (?) |
| Sterne | Talente ziehen (1 Stern = 1 Talent) | (?) vermutlich Stage-Abschluss |
| Stadtmünzen | Basislager ausbauen | Stadtmünzen-Schneider, Überfälle |
| Schlüssel (Silber, Gold) | Truhen öffnen | Pakete, (?) |
| Schraubenschlüssel | (?) | Pakete |
| Event-Münzen | Event-Held (Drako, 1000 Stück) | Event |
| Schilde (max. 3) | Schutz vor Überfällen | (?), kaufbar |
| Battle-Pass-Punkte | Battle-Pass-Stufen | (?) |

Das sind **über 12 Ressourcen**. Für ein Hobby- bzw. Erstprojekt sind das deutlich zu viele, siehe Abschnitt 10.

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

1. **Der Kampf selbst:** Was macht der Finger? Tippt oder wischt man an der Trommel, verteilt man Patronen, platziert man Helden? Am besten 3–4 Bilder direkt hintereinander und ein Satz dazu.
2. **„Spielmodus“:** Boss Rush und Survival
3. **Ende eines Runs:** Sieg, Niederlage, Belohnungen
4. **Detailansicht eines Helden:** Kosten fürs Aufwerten, Werte, alle 4 Fähigkeiten
5. **Überfall:** wie er abläuft
6. Battle Pass, Glücksrad, Truhen, Tagesmissionen
7. Einstellungen (Tempo, Ton, Vibration)

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
