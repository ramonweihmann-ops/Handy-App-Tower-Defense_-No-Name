# Fünkchen · Vorlagen für das 3D-Modell

- [Vorderansicht](fuenkchen_vorn.png)
- [Linkes Profil](fuenkchen_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](fuenkchen_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. Vier Beine, halb ausgebreitete Flügel und ein nach hinten gerichteter Schwanz.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/fuenkchen.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Fünkchen war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle · 16.11.2026

Ein Erzeugungsversuch für 30 Credits. Meshy 7.1, hohe Detailtiefe, Standardauflösung, Multi-View mit Vorderseite, linkem Profil und Rückseite, Texturmodell Meshy 7 mit 2K-Texturen, privat, Pose aus und Bildverbesserung an. Die 10K-Reduktion war kostenlos und nutzt feste Dreiecks-Topologie.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [fuenkchen_original_statisch.glb](fuenkchen_original_statisch.glb) | 406.680 |
| [fuenkchen_reduziert_statisch.glb](fuenkchen_reduziert_statisch.glb) | 10.336 |

Alle GLBs sind direkte Meshy-Exporte mit drei eingebetteten 2K-Texturen.

**Rigging:** Für dieses Modell ist der statische Export vorgesehen.

**Sichtprüfung:** Vier Beine und zwei Flügel. Schweif und Rückenstacheln sind in der Seiten- und Draufsicht erkennbar. Die Flügel setzen seitlich am Rücken an.

Die Vorschauen zeigen das reduzierte statische Modell aus Blender.
[Vorn](fuenkchen_vorschau_vorn.png) · [Seite](fuenkchen_vorschau_seite.png) · [Oben](fuenkchen_vorschau_oben.png) · [Hinten](fuenkchen_vorschau_hinten.png)

**Für den Einbau:** Das Skelett und den Flügelschlag baut Claude. Der Godot-Import und die Spielanimationen sind noch offen.
