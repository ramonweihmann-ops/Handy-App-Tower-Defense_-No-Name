# Borkenkäfer – zweiter Versuch, sechs Beine

Stand: 10.11.2026. Die neue Draufsicht wurde mit der eingebauten Bildgenerierung aus dem freigegebenen Borkenkäfer und der erfolgreichen Panzerkäfer-Draufsicht erstellt. Die tatsächliche Meshy-Eingabe liegt als `borkenkaefer_vorlage_oben.png` bei (1024 × 1024, RGBA).

## Kosten und Erzeugung

- Genau eine Erzeugung: **15 Meshy-Credits**, Guthaben 1.330 → 1.315.
- Bild-zu-3D, Meshy T2.5, Smart Topology, Ziel 10.000 Polygone.
- Ein Eingabebild, kein Zusatztext; Texturen an (Meshy N1, 2K), Posekorrektur aus, privat.
- Kein Rigging und keine Bewegungen gebucht. Skelett und Animationen fehlen entsprechend absichtlich.
- `borkenkaefer_statisch_roh.glb` ist die unveränderte heruntergeladene Datei.

## Prüfung

- glTF 2.0, 10.055 Dreiecke, ein Material, eine eingebettete Textur 2048 × 2048.
- Vorlage: genau **sechs Beine**, drei pro Seite.
- Rohmodell: genau **sechs Beine mit sechs eigenen Füßen**, drei pro Seite; anhand aller vier beigefügten Ansichten geprüft. Die Unteransicht bestätigt die sechs Ansätze, kein verborgenes viertes Paar.
- Vorder- und Seitenansicht zeigen die sechs Beine teilweise in erhöhter, steifer Stellung. Claude muss die Ruhepose beim eigenen Rigging auf eine natürliche Standfläche bringen. Das Rohmodell wurde dafür nicht verändert.
- Gesicht, Rindenpanzer und Moospolster entsprechen der Eingabe. Die Rinde ist weich vereinfacht. Keine auffälligen losen Netzspitzen gesehen; keine technische Garantie für vollständig bereinigte Topologie.
- Kein Godot-Test durchgeführt. Die Textur ist absichtlich noch 2K; Verkleinerung auf den Spielstandard übernimmt Claude.

Die vier PNG-Vorschauen sind transparente orthografische Render des tatsächlichen GLB, keine neu gezeichneten Ansichten. Die Orientierung der Rohgeometrie wurde beim Import beibehalten; die Beine erscheinen deshalb von oben teils verkürzt. Die Unteransicht ist zur Anatomieprüfung gedacht.

SHA-256 der unveränderten GLB: `634c9c928c7799a98999a8832443576dc198f02b42c3c313b507dc7d8cf8eed5`.

Die frühere Version mit acht Beinen bleibt unberührt und wird durch dieses Paket nicht als brauchbar erklärt.
