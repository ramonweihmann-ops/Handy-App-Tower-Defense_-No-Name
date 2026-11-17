# Fritzi · Vorlagen für das 3D-Modell

- [Vorderansicht](fritzi_vorn.png)
- [Linkes Profil](fritzi_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](fritzi_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. A-Pose mit gestreckten Armen, geraden Beinen und leeren Händen.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/fritzi.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Fritzi war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle H3

Erzeugung am 16.11.2026. Ein Durchlauf für 30 Credits je Champion. Meshy 7.1, Bild zu 3D mit Vorderansicht, linkem Profil und Rückansicht, Standardauflösung, Meshy-7-Texturmodell mit 2K, privat, Bildverbesserung ein, Pose aus. Die Reduktion auf das feste 10K-Dreiecksziel war kostenlos.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [fritzi_original_statisch.glb](fritzi_original_statisch.glb) | 516.422 |
| [fritzi_reduziert_statisch.glb](fritzi_reduziert_statisch.glb) | 10.345 |
| [fritzi_rig_roh.glb](fritzi_rig_roh.glb) | 10.345 |

**Sichtprüfung.** Ein Kopf, zwei Arme, zwei Beine. Beide Hände sind leer und vom Rumpf getrennt. Bei den vier Ansichten sind keine abgelösten Körperteile oder offensichtlichen Öffnungen an Kopf oder Kopfbedeckung sichtbar. Orange Mütze, braune Weste und rückwärtiger Gurt sind sichtbar. Die Mütze wirkt im Blender-Prüflicht heller als in der Vorlage.

[Vorn](fritzi_vorschau_vorn.png) · [Seite](fritzi_vorschau_seite.png) · [Oben](fritzi_vorschau_oben.png) · [Hinten](fritzi_vorschau_hinten.png)

**Rigging.** Meshys humanoides Rigging war erfolgreich. Der GLB-Export nutzt MeshyRig und enthält eine Hautbindung mit 32 Gelenken sowie die von Meshy beigefügten Clips `Running` und `Walking`. Das angezeigte Guthaben blieb bei 925 Credits. Verformungen und Godot-Import stehen noch aus.
