# Panzerkäfer – zweiter Modelltest mit sechs Beinen

Stand: 03.11.2026. Ergebnis der visuellen Geometrieprüfung: **genau sechs Beine, drei pro Seite**. Alle sechs cremefarbenen Füße sind in der orthografischen Draufsicht getrennt erkennbar; die Unteransicht bestätigt die drei Beinpaare. Das alte Acht-Bein-Modell unter `Modelltests_v1/` bleibt unverändert erhalten.

## Lieferung

- `panzerkaefer_statisch_roh.glb`: unveränderte statische Meshy-Download-Datei, glTF 2.0, ohne Skelett und ohne Animationen.
- `panzerkaefer_draufsicht_pruefung.png`: tatsächliches Modell von senkrecht oben, 1024 × 1024, transparente Umgebung.
- `panzerkaefer_unterseite_pruefung.png`: zusätzliche Unteransicht zur Kontrolle der Beinpaare.
- `panzerkaefer_modellvorschau.png`: räumliche Vorschau des Rohmodells.
- `panzerkaefer_vorlage_vorn.png`: die bisherige korrigierte Vorderansicht mit sechs Beinen.
- `panzerkaefer_vorlage_oben.png`: neue, ausdrücklich mit drei Beinen pro Seite erzeugte Draufsicht; diese war die tatsächlich verwendete Meshy-Eingabe.
- Prüfberichte und die dafür verwendeten Skripte sowie die Bildanweisung für die zusätzliche Draufsicht.

## Erzeugung und technische Abweichung

Ein einzelner neuer Erzeugungsversuch, **15 Meshy-Credits**, Meshy T2.5, Smart Topology, Ziel 10.000 Polygone, Texturen an, Posekorrektur aus, privat. Kein Rigging beauftragt und keine Adobe-Dienste genutzt.

Die Vorgabe in `../PANZERKAEFER_NEU_FUER_CHATGPT.md` nennt Vorder- und Draufsicht als zwei Eingaben sowie eine zusätzliche Textanweisung. Die tatsächlich verfügbare T2.5-Maske bietet jedoch nur einen Bildplatz und kein Textfeld. Mehransichten waren in einem anderen Modellmodus verfügbar, dort wurden 35 statt 15 Credits angezeigt. Um im vorgesehenen T2.5-Versuch zu bleiben, wurde ausschließlich die eindeutige neue Draufsicht eingelesen. Es wurden weder zwei Ansichten gleichzeitig noch der Zusatztext an Meshy übermittelt. Beide Bildvorlagen sind für die Nacharbeit enthalten. Der andere Modellmodus wurde nicht zur Erzeugung verwendet.

## Dateiprüfung

- 3.154.968 Bytes, **10.444 Dreiecke**, ein Netz und ein Material.
- Eine eingebettete Basisfarbtextur mit 2048 × 2048 Pixeln. Rohdatei absichtlich unverändert; für das Handy vor dem Einbau auf 1024 × 1024 bringen.
- Keine Skelette, keine vorhandenen Animationsclips, keine externen Texturdateien erforderlich.
- Import in Blender erfolgreich; alle geprüften Modellkoordinaten sind endlich.
- Ausdehnung nach Blender-Import ungefähr 0,950 × 0,691 × 0,416 Einheiten. Modell noch auf die passende Gegnergröße skalieren und Bodenkontakt einrichten.
- SHA-256 der GLB: `f52a433edbc5dd1b75b697573a51392cbec632cbfe1c288ca7ebc5cb9fd0aa4e`.

## Nacharbeit für Claude

Die Beinzahl ist freigeprüft; das ist noch keine Freigabe als fertiges Spielmodell. Am mittleren Bein befindet sich ein kleiner dünner spitzer Netzfortsatz, sichtbar in Ober- und Unteransicht. Das ist ein Erzeugungsartefakt, kein weiteres Bein. Vor dem Rigging entfernen und die Beinansätze beziehungsweise die Unterseite auf saubere Verformung prüfen. Die Textur wirkt teilweise weich und darf bei der Nacharbeit geglättet oder vereinfacht werden.

Danach wie von Claude vorgesehen: Skelett für drei Beinpaare aufbauen, Dreifuß-Gang `Walk` und Biss `Attack` erstellen und im Spiel testen. Bodenhöhe, Ausrichtung, Gegnermaßstab und Bewegungsablauf wurden hier noch nicht im laufenden Godot-Spiel geprüft. Die sechs Beine wurden aus dem tatsächlichen importierten Modell kontrolliert, nicht nur aus dem Eingabebild.
