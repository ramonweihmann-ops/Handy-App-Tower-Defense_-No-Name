# Champions als Comic-Modelle – Aufträge für ChatGPT (Stand 16.11.2026)

Konzept: `docs/HELDEN_UND_SCHUESSE.md`. Vorbild ist Dusty Jo (`Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/`).

- **Teil A – Vorlagen für alle elf Champions:** kostenlos (eingebaute Bildgenerierung).
- **Teil B – Meshy-Modelle für Fünkchen, Pip, Rollo und Nova:** vom Nutzer am 16.11.2026 freigegeben,
  höchstens 4 Erzeugungen zu je etwa 30 Credits, zusammen etwa 120 Credits. Erst nach Teil A abschicken.
  Die übrigen sieben Champions brauchen eine eigene Freigabe.

---

## Teil A: Text für ChatGPT

Bitte für mein Handyspiel (Tower Defense, Comic-Stil) Bildvorlagen für 3D-Modelle von elf Champions erstellen.
Vorbild ist unser fertiger Champion Dusty Jo: Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4, Ordner Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/ (dusty_jo_vorn.png,
dusty_jo_links.png, dusty_jo_hinten.png). Genau so bitte für jeden der elf Champions.

Aussehen: genau wie die Heldenbilder im Spiel, Ordner game/ui/heroes2d/ (iska.png, brocken.png, volta.png,
kalle.png, margot.png, lynx.png, fritzi.png, fuenkchen.png, pip.png, rollo.png, nova.png). Gleiche Figur, gleiche
Farben, gleiche Frisur und Kleidung, gleicher kindgerechter Comic-Stil mit großem Kopf. Bitte von dort laden.

JE CHAMPION DREI BILDER
- <id>_vorn.png: von vorn
- <id>_links.png: von der linken Seite
- <id>_hinten.png: von hinten (besonders wichtig, so sieht man die Figur im Spiel am häufigsten)

FÜR ALLE MENSCHEN (Iska, Brocken, Volta, Kalle, Margot, Lynx, Fritzi, Nova)
- A-Pose: Arme etwa 40 Grad vom Körper abgespreizt, Ellbogen gestreckt, Beine gerade und hüftbreit
- klare Lücken zwischen Armen und Körper und zwischen den Beinen
- **leere Hände, keine Waffe, kein Gerät in der Hand** (die Waffe wird getrennt gebaut). Hut, Mütze, Gurte und
  Taschen bleiben, aber fest am Körper.
- Haare eng am Kopf, Pferdeschwänze nicht frei abstehend

SONDERFORMEN
- fuenkchen (lila Drache): steht auf vier Beinen, Flügel halb ausgebreitet und klar vom Körper getrennt, Schwanz
  gerade nach hinten, Maul geschlossen
- pip (Roboter): A-Pose wie oben, Hände leer (ohne Schraubenschlüssel), Antenne gerade
- rollo (Panzer): wie im Bild, Kanone nach vorn, Ketten gut sichtbar; keine Pose nötig

FORMAT
- je 1254 × 1254 Pixel, PNG mit durchsichtigem Hintergrund, eine Figur, etwa 10 % Rand
- orthografisch, keine Bodenplatte, kein Schatten, keine Schrift
- alle drei Ansichten einer Figur in gleicher Größe und Höhe, damit sie zusammenpassen

BITTE LIEFERN je Champion in Vorlage_Raw/Helden_Roh/<id>_comic_v1/ (id: iska, brocken, volta, kalle, margot, lynx,
fritzi, fuenkchen, pip, rollo, nova): die drei Bilder und eine kurze LIESMICH_CLAUDE.md. Dazu
Vorlage_Raw/Helden_Roh/UEBERSICHT_VORLAGEN.png mit allen 33 Bildern.

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.

---

## Teil B: Text für ChatGPT (erst nach Teil A)

Bitte aus den neuen Vorlagen bei Meshy 3D-Modelle für vier Champions erzeugen, genau wie damals bei Dusty Jo
(Vorlage_Raw/Helden_Roh/dusty_jo_comic_v1/LIESMICH_CLAUDE.md). Repository Handy-App-Tower-Defense_-No-Name, Branch
claude/amazing-hypatia-yl59v4.

KOSTENRAHMEN: vom Nutzer freigegeben, höchstens 4 Erzeugungen zu je etwa 30 Credits (zusammen etwa 120 Credits).
Je Champion ein Versuch; wenn er misslingt, melden statt neu erzeugen. Wenn Rigging oder Bewegungen extra kosten,
vorher melden und nicht ungefragt buchen.

DIE VIER CHAMPIONS (Vorlagen in Vorlage_Raw/Helden_Roh/<id>_comic_v1/)
- fuenkchen: lila Drache auf vier Beinen mit zwei Flügeln · kein Rigging (Claude baut Skelett und Flügelschlag)
- pip: Roboter, A-Pose · humanoides Auto-Rigging versuchen; scheitert es, das Intelligente Rig (Beta) wie bei Dusty Jo
- rollo: Panzer mit Ketten und Kanone · kein Rigging
- nova: Mensch, A-Pose · humanoides Auto-Rigging versuchen; scheitert es, das Intelligente Rig (Beta) wie bei Dusty Jo

ERZEUGUNG
- Meshy 7.1 Bild zu 3D mit Multi-View aus den drei Ansichten (vorn, links, hinten), Standardauflösung,
  Texturen 2K, privat
- danach die kostenlose 10K-Reduktion speichern (Voraussetzung für das Rigging)

VOR DEM HOCHLADEN PRÜFEN
- jedes Modell von vorn, von der Seite, von oben und **von hinten** rendern
- Gliedmaßen zählen: Fünkchen vier Beine und zwei Flügel, Pip und Nova zwei Arme und zwei Beine, Rollo zwei Ketten
- Rückseite muss zur Vorlage passen (keine verschmolzenen oder fehlenden Teile)

ABLAGE in Vorlage_Raw/Helden_Roh/<id>_comic_v1/ je Champion:
- <id>_original_statisch.glb (unverändert), <id>_reduziert_statisch.glb (10K)
- bei Rigging zusätzlich <id>_rig_roh.glb
- <id>_vorschau_vorn.png, _seite.png, _oben.png, _hinten.png
- Ergänzung in LIESMICH_CLAUDE.md: verbrauchte Credits, Einstellungen, Dreiecke, gezählte Gliedmaßen, Rigging-Ergebnis
