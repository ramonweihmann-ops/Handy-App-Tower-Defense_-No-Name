# Nova · Vorlagen für das 3D-Modell

- [Vorderansicht](nova_vorn.png)
- [Linkes Profil](nova_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](nova_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. A-Pose mit gestreckten Armen, geraden Beinen und leeren Händen.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/nova.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Nova war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle · 16.11.2026

Ein Erzeugungsversuch für 30 Credits. Meshy 7.1, hohe Detailtiefe, Standardauflösung, Multi-View mit Vorderseite, linkem Profil und Rückseite, Texturmodell Meshy 7 mit 2K-Texturen, privat, Pose aus und Bildverbesserung an. Die 10K-Reduktion war kostenlos und nutzt feste Dreiecks-Topologie.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [nova_original_statisch.glb](nova_original_statisch.glb) | 599.598 |
| [nova_reduziert_statisch.glb](nova_reduziert_statisch.glb) | 10.437 |
| [nova_rig_roh.glb](nova_rig_roh.glb) | 10.437 |

Alle GLBs sind direkte Meshy-Exporte mit drei eingebetteten 2K-Texturen.

**Rigging:** Humanoides Auto-Rigging erfolgreich und kostenlos. Die Leistenmarkierung wurde manuell an der Figur ausgerichtet. Export mit einer Hautbindung, 64 Gelenken und Meshys Mixamo-Skelettvorlage. Meshy hat `Running`, `Walking` automatisch mit exportiert. Für die Clips fiel keine Zusatzbuchung an.

**Sichtprüfung:** Zwei Arme, zwei Beine und leere Hände. Rückseite mit Haarreif, dichtem Lockenvolumen und sichtbar getrennten Armen und Beinen.

Die Vorschauen zeigen das reduzierte statische Modell aus Blender.
[Vorn](nova_vorschau_vorn.png) · [Seite](nova_vorschau_seite.png) · [Oben](nova_vorschau_oben.png) · [Hinten](nova_vorschau_hinten.png)

**Für den Einbau:** Bewegungstest an Schulterplatten, Hüfte und Stiefeln durchführen. Der Godot-Import und die Spielanimationen sind noch offen.
