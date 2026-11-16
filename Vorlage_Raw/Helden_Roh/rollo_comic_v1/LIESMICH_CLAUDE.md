# Rollo · Vorlagen für das 3D-Modell

- [Vorderansicht](rollo_vorn.png)
- [Linkes Profil](rollo_links.png), die Vorderseite zeigt im Bild nach links
- [Rückansicht](rollo_hinten.png), als Referenz für die häufigste Ansicht im Kampf

Drei PNGs mit 1254 × 1254 Pixeln, transparentem Hintergrund und gleicher Motivhöhe. Kettenfahrzeug mit nach vorn gerichteter Kanone.

Die eingebaute Bildgenerierung hat das [Heldenbild im Spiel](../../../game/ui/heroes2d/rollo.png) als Vorlage für Figur, Farben und Kleidung verwendet. [Dusty Jo](../dusty_jo_comic_v1) diente als Maßstab für Stil und Kamerawinkel. Die Vorderansicht von Rollo war die zusätzliche Referenz für Profil und Rückansicht.

Beim Modellieren Vorder- und Rückansicht auf dieselbe Körperachse ausrichten. Für die Tiefe das Profil heranziehen. Schmuck, Gurtzeug und Taschen gehören zur Figur. Separates Zubehör wie gehaltene Geräte und Waffen bei den Menschen erhält eigene Modelle.

## Meshy-Rohmodelle · 16.11.2026

Ein Erzeugungsversuch für 30 Credits. Meshy 7.1, hohe Detailtiefe, Standardauflösung, Multi-View mit Vorderseite, linkem Profil und Rückseite, Texturmodell Meshy 7 mit 2K-Texturen, privat, Pose aus und Bildverbesserung an. Die 10K-Reduktion war kostenlos und nutzt feste Dreiecks-Topologie.

| Datei | Gemessene Dreiecke |
| --- | --- |
| [rollo_original_statisch.glb](rollo_original_statisch.glb) | 380.056 |
| [rollo_reduziert_statisch.glb](rollo_reduziert_statisch.glb) | 9.900 |

Alle GLBs sind direkte Meshy-Exporte mit drei eingebetteten 2K-Texturen.

**Rigging:** Für dieses Modell ist der statische Export vorgesehen.

**Sichtprüfung:** Zwei klar getrennte Ketten und eine Kanone. Meshy hat den weißen Stern auch auf die Rückseite übertragen und dort ein blasses Muster auf den Turm gelegt. Die Rückseite der Vorlage ist an diesen Stellen einfarbig.

Die Vorschauen zeigen das reduzierte statische Modell aus Blender.
[Vorn](rollo_vorschau_vorn.png) · [Seite](rollo_vorschau_seite.png) · [Oben](rollo_vorschau_oben.png) · [Hinten](rollo_vorschau_hinten.png)

**Für den Einbau:** Für den Spielimport die Vorwärtsachse prüfen. Das Modell zeigt im Blender-Import entlang −X nach vorn. Rückwärtigen Stern und Muster bei der Texturüberarbeitung entfernen. Der Godot-Import und die Spielanimationen sind noch offen.
