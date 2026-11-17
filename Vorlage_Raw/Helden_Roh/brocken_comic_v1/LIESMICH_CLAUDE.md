# Brocken · Vorlagen für das 3D-Modell

- [Vorderansicht](brocken_vorn.png)
- [Linkes Profil](brocken_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](brocken_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. A-Pose mit gestreckten Armen, geraden Beinen und leeren Händen.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/brocken.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Brocken war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle H3

Erzeugung am 16.11.2026. Ein Durchlauf für 30 Credits je Champion. Meshy 7.1, Bild zu 3D mit Vorderansicht, linkem Profil und Rückansicht, Standardauflösung, Meshy-7-Texturmodell mit 2K, privat, Bildverbesserung ein, Pose aus. Die Reduktion auf das feste 10K-Dreiecksziel war kostenlos.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [brocken_original_statisch.glb](brocken_original_statisch.glb) | 394.428 |
| [brocken_reduziert_statisch.glb](brocken_reduziert_statisch.glb) | 10.300 |
| [brocken_rig_roh.glb](brocken_rig_roh.glb) | 10.300 |

**Sichtprüfung.** Ein Kopf, zwei Arme, zwei Beine. Beide Hände sind leer und vom Rumpf getrennt. Bei den vier Ansichten sind keine abgelösten Körperteile oder offensichtlichen Öffnungen an Kopf oder Kopfbedeckung sichtbar. Die gelbe Mütze sitzt auf dem Kopf. Beide rückwärtigen Latzhosengurte sind sichtbar. Meshy hat über dem unteren Rücken zusätzliche braune Schlaufen und helle Beschläge gezeichnet.

[Vorn](brocken_vorschau_vorn.png) · [Seite](brocken_vorschau_seite.png) · [Oben](brocken_vorschau_oben.png) · [Hinten](brocken_vorschau_hinten.png)

**Rigging.** Der erste humanoide Versuch ist in Meshy fehlgeschlagen. Das intelligente Rig (Beta) war erfolgreich. Der GLB-Export hat eine Hautbindung mit 44 Gelenken und generische Knochennamen. Meshy liefert bei diesem Rig keine Bibliotheksbewegungen. Das Guthaben blieb bei 925 Credits. Verformungen und Godot-Import stehen noch aus.
