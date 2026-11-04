# Explosionen v2 – ernsthafterer Stil

Der Nutzer hat die neue Stilprobe von Brockens Raketenexplosion gegenüber v1 bevorzugt. Diese Fassung überträgt die Richtung auf die Luftangriff-Explosionsreihe und Rollos Wucht-Einschlag. Diese beiden abgeleiteten Motive sind neue Vorschläge. Keine generelle neue Freigabe aller Kampfeffekte.

## Einbau

Dieses Paket ergänzt `Effekte_ChatGPT_v1` und ersetzt ausschließlich die Grafik der drei gleichnamigen Effekte: `brocken_explosion`, `luftangriff_explosionsreihe`, `rollo_einschlag`. Alle anderen Effekte, Jäger, Schüsse und Figuren bleiben in v1. Die alte Fassung bleibt zum Vergleich bestehen. Keine Spieldateien wurden geändert.

Je Effekt: transparentes RGBA-PNG, 16 Phasen à 256 × 256, Raster 4 × 4, Blatt 1024 × 1024. Reihenfolge links nach rechts, dann nächste Zeile. Gerades Alpha, sRGB, Mischung `alpha`, 24 Bilder/s, einmal abspielen, danach ausblenden. JSON-Schlüssel und normierter Anker `[0.5, 0.5]` entsprechen v1. Weltbreiten: Brocken 2,5 m, Luftangriff 8 m, Rollo 1,7 m. Ausrichtung als Billboard zur festen Kampf-Kamera. Größen bitte im echten Spiel kalibrieren.

Mehr Wucht durch heißere Lichtkerne, kantige Flammen, kurze Funken und dunkle Rauch-/Staubfetzen. Keine zusätzlichen Schadenszonen, Treffer oder Spielmechaniken. Die Luftangriff-Reihe enthält bereits drei Zündstellen; alternativ einzelne Brocken-Explosionen zeitversetzt an den Weltpositionen abspielen.

GIFs zeigen dieselben Phasen auf dunkelviolettem Prüfgrund, weil GIF weiche Transparenz nicht sauber darstellen kann. Dieser Grund ist nicht im PNG. Die Einzel-GIFs wiederholen zur Prüfung; maßgeblich sind `fps` und `loop` im JSON. Die gemeinsame animierte Übersicht pausiert am Ende kurz. Übersichten sind Brückenmontagen und **keine Godot-Spieltests**. Raster, Transparenz, Bildgrößen und GIF-Phasen wurden geprüft. Überlagerung, Tempo und Wirkung im Kampf muss Claude auf der Prüfseite kontrollieren.

Erzeugt mit eingebauter Bildgenerierung im vorhandenen Konto, ohne Meshy oder zusätzliche kostenpflichtige Dienste. Technisch gerastert, gemeinsam pro Folge skaliert und am Mittelpunkt registriert. Die Prompts stehen in `BILDANWEISUNGEN.json`. Keine Fremdasset-Effekte verwendet. Nutzung im Rahmen der Bedingungen des verwendeten Kontos; keine Zusicherung rechtlicher Exklusivität KI-generierter Motive. Brückenhintergrund aus dem vorhandenen Projektbestand.
