# Kampfeffekte: Auftrag für ChatGPT (Stand 04.11.2026)

Ziel: Schüsse, Einschläge, Explosionen und Superfähigkeiten sollen mehr Action und Charakter bekommen, jede
Waffe erkennbar anders. ChatGPT liefert einen **eigenen Vorschlag als fertige Bildfolgen**; Claude baut parallel
eine Fassung aus Godot-Partikeln. Danach vergleichen wir beide im Spiel und nehmen die bessere (oder mischen).

**Keine kostenpflichtigen Dienste ohne Rückfrage beim Nutzer.** Bildgenerierung im bestehenden Konto ist in
Ordnung; Meshy nur, wenn unten ausdrücklich ein 3D-Modell verlangt ist, und vorher Credits nennen.

## Wie die Effekte im Spiel sitzen

- Kampf in 3D, feste Kamera schräg von hinten oben über die Brücke (etwa 50° nach unten geneigt), Helden unten
  am Energiezaun, Gegner kommen von oben aus dem Wurmloch. Die Effekte erscheinen als **flache Bilder, die immer
  zur Kamera zeigen** (Billboards). Darum: jeden Effekt so zeichnen, wie man ihn **schräg von oben** sieht.
- Bildschirm hochkant (Handy), Effekte sind klein bis mittel: ein Mündungsfeuer ist auf dem Handy etwa 40–80 px
  groß, eine Raketenexplosion 150–250 px, der Luftangriff fast bildschirmbreit.
- Stil wie die freigegebenen Comic-Grafiken (Icons_v1, Helden, Monster): kräftige Farben, weiche Comic-
  Schattierung, klare dunkle Kontur nur dort, wo sie hilft; keine fotorealistischen Rauchwolken, kein Blut.

## Dateiformat (wichtig, sonst kann das Spiel es nicht abspielen)

- **Bildfolge als Sprite-Sheet:** eine PNG-Datei mit transparentem Hintergrund (RGBA, nicht vormultipliziertes
  Alpha), alle Einzelbilder gleich groß in einem Raster, Reihenfolge links nach rechts, dann nächste Zeile.
- Einzelbildgröße: **256 × 256** (kleine Effekte wie Mündungsfeuer, Funken: **128 × 128**). Ganzes Sheet höchstens
  **2048 × 2048**. 8 bis 16 Bilder je Effekt reichen (bei 24 Bildern pro Sekunde).
- Der Effekt steht in jedem Bild an derselben Stelle (Ankerpunkt fest, z. B. Mündung am linken Rand mittig,
  Explosion in der Bildmitte), damit nichts springt. Rand von ein paar Pixeln frei lassen, nichts abschneiden.
- Je Effekt eine kleine JSON-Datei daneben:
  `{"name": "rakete_explosion", "frames": 16, "cols": 4, "rows": 4, "fps": 24, "loop": false,
  "anker": [0.5, 0.5], "groesse_m": 2.5, "mischung": "alpha" oder "additiv", "notiz": "…"}`
  (`groesse_m` = ungefähre Breite im Spiel in Metern; ein Held ist etwa 1,5 m hoch, die Brücke etwa 9 m breit.)
- Leuchtende Teile (Blitze, Plasma, Feuer) dürfen als eigene Ebene „additiv“ kommen: dann Schwarz statt
  Transparenz als Hintergrund und im JSON `"mischung": "additiv"`.
- Zu jedem Effekt eine **Vorschau-GIF** (gleiche Bilder, Endlosschleife), damit der Nutzer prüfen kann.

## Was gebraucht wird

Helden und Waffen (Spieldaten):

| Held | Waffe | Art | Mündung | Geschoss | Einschlag |
|---|---|---|---|---|---|
| Dusty Jo | Revolver | 6 Schuss, der letzte fächert auf | kurzer gelber Blitz | Leuchtspur | kleine Funken |
| Iska | Maschinengewehr | Dauerfeuer | schnelles Flackern (3 Varianten) | dünne Leuchtspuren | Funkenregen |
| Brocken | Raketenwerfer | Flächenschaden | Rauchstoß nach hinten | Rakete mit Rauchschweif | **große Explosion** + Druckwelle |
| Volta | Funkenpistole | Kettenblitz | blauer Funke | Blitzbogen (dehnbar) | Zucken am Gegner |
| Kalle | Frostpistole | verlangsamt | Frostwolke | Eiskristall-Strahl | Eis splittert, Frost bleibt kurz |
| Käpt'n Margot | Schrotflinte | stark aus der Nähe | breiter Blitz + Rauch | Schrotkegel | mehrere kleine Treffer |
| Lynx | Präzisionsgewehr | durchschlägt mehrere | heller Blitz | lange gerade Spur | Durchschuss-Funken |
| Fritzi | Brandflinte | Feuerkegel, setzt in Brand | Feuerstoß | Flammenkegel (Schleife) | Brennen am Gegner (Schleife) |
| Fünkchen | Sternenatem (Drache) | Strahl durch die Reihe | Glühen am Maul | Sternenstrahl (dehnbar, Schleife) | Sternenfunken |
| Pip | Schraubenwerfer | repariert den Schild | Klack | fliegende Schraube (dreht) | Metallfunken; Reparatur-Funkeln am Zaun |
| Rollo | Wuchtkanone | stößt zurück | Kanonenblitz | Kugel | Aufprall-Ring, Staub |
| Nova | Raketenfäuste | zieht zusammen, bremst | Antriebsflamme | fliegende Faust | lila Sog-Wirbel |

Dazu für alle:

1. **Gegner besiegt:** Comic-„Zerplatzen“ mit Glibber/Sternchen in drei Farben (grün, lila, rosa), ohne Blut.
2. **Boss besiegt:** größere Version mit Lichtstrahlen.
3. **Treffer am Energiezaun** (Gegner schlägt zu): Funken + kurzes Aufleuchten.
4. **Kritischer Treffer:** kleines „KRIT!“-Aufblitzen als Bild (Schrift zeichnet das Spiel, nur der Blitz-Stern).
5. **Luftangriff (Superfähigkeit):** zwei oder drei kleine Raumjäger fliegen von unten nach oben über die Brücke,
   werfen Bomben, danach eine Reihe Explosionen über die ganze Breite.
   - Raumjäger als **Sprite schräg von oben** (eine Ansicht, 512 × 512, mit kleinem Triebwerksglühen als eigene
     Bildfolge), im Comic-Stil der Station (lila/weiß/gelb).
   - Alternativ als 3D-Modell (GLB, höchstens 3.000 Dreiecke, Textur 1024, Blick +Z): nur nach Rückfrage
     beim Nutzer wegen Meshy-Credits.
   - Bombe (kleines Sprite) und „Explosionsreihe“ (eine breite Bildfolge oder mehrere Explosionen zum Versetzen).
6. **Medipack (Booster):** grün leuchtende Kreuze und Heilringe am Zaun.

## Ablage

`Vorlage_Raw/Effekte_ChatGPT_v1/` mit je Effekt einem Ordner `<name>/`:
`<name>_sheet.png`, `<name>.json`, `<name>_vorschau.gif`. Dazu eine **Übersicht** `UEBERSICHT.png` (alle Effekte
auf einem Bild, über ein Bildschirmfoto der Brücke gelegt, damit Größe und Wirkung sichtbar sind) und
`LIESMICH_CLAUDE.md` (was enthalten ist, wie erzeugt, Lizenz/Nutzungsrechte, Auffälligkeiten).

Reihenfolge, falls nicht alles auf einmal geht: Brocken-Explosion, Luftangriff, Gegner besiegt, dann die
übrigen Helden.

## Danach

Claude baut die Bildfolgen ein (Godot: AnimatedSprite3D bzw. eigener Billboard-Shader), stellt sie neben die
eigene Partikel-Fassung und macht eine Prüfseite mit beiden im echten Kampf. Der Nutzer entscheidet je Effekt.
