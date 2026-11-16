# Pip · Vorlagen für das 3D-Modell

- [Vorderansicht](pip_vorn.png)
- [Linkes Profil](pip_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](pip_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. Roboter in A-Pose mit leeren Greifern und aufrechter Antenne.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/pip.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Pip war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle · 16.11.2026

Ein Erzeugungsversuch für 30 Credits. Meshy 7.1, hohe Detailtiefe, Standardauflösung, Multi-View mit Vorderseite, linkem Profil und Rückseite, Texturmodell Meshy 7 mit 2K-Texturen, privat, Pose aus und Bildverbesserung an. Die 10K-Reduktion war kostenlos und nutzt feste Dreiecks-Topologie.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [pip_original_statisch.glb](pip_original_statisch.glb) | 343.540 |
| [pip_reduziert_statisch.glb](pip_reduziert_statisch.glb) | 10.299 |
| [pip_rig_roh.glb](pip_rig_roh.glb) | 10.299 |

Alle GLBs sind direkte Meshy-Exporte mit drei eingebetteten 2K-Texturen.

**Rigging:** Humanoides Auto-Rigging erfolgreich und kostenlos. Die Leistenmarkierung wurde manuell an der Figur ausgerichtet. Export mit einer Hautbindung, 44 Gelenken und Meshys Mixamo-Skelettvorlage. Meshy hat `Running`, `Walking` automatisch mit exportiert. Für die Clips fiel keine Zusatzbuchung an.

**Sichtprüfung:** Zwei Arme mit zwei Greifern, zwei Beine, eine Antenne. Die orange Rückenplatte aus der Vorlage fehlt im exportierten Material. Der rückwärtige Körperumriss passt.

Die Vorschauen zeigen das reduzierte statische Modell aus Blender.
[Vorn](pip_vorschau_vorn.png) · [Seite](pip_vorschau_seite.png) · [Oben](pip_vorschau_oben.png) · [Hinten](pip_vorschau_hinten.png)

**Für den Einbau:** Greifer und kurze Beine beim Bewegungstest auf Verformungen und Überschneidungen prüfen. Die orange Rückenplatte bei der Texturüberarbeitung ergänzen. Der Godot-Import und die Spielanimationen sind noch offen.
