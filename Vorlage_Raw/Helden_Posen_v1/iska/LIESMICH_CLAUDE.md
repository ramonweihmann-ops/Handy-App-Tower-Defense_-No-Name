# iska · Vergleichsfassung der Champion-Posen

Kompakter Blaster quer vor dem Körper. Die linke Hand stützt am Vorderschaft. Die türkisfarbene Frontlinse bestimmt den Mündungspunkt.

## Skelett und Export

Kostenloses Neu-Rigging in Meshy mit manuell korrigierter Leiste durchgeführt. Meshy lieferte nur Handknochen. In Blender wurden je Hand zwei Gelenke für die zusammenhängende Fingerpartie ergänzt und gewichtet. Die Geometrie modelliert diese Partie als zusammenhängende Form.

- **Dreiecke gesamt.** 13222, einschließlich Waffe und gegebenenfalls Tablet.
- **Aktionen.** Pose als statische Menüpose und Shoot als 0,4-s-Zyklus mit Zielhaltung, kurzer Bewegung und Rückkehr auf den Startwert.
- **Koordinaten.** Ausgangsfigur 2,0 Einheiten hoch, Füße am Boden. Vorwärts in Blender ist −Y. Der GLB-Export nutzt +Y als Hochachse.
- **Waffe.** mixamorig:RightHand → WeaponSocket → Weapon → Muzzle. Der lokale −Z-Vektor des GLB-Mündungsknotens folgt der Längsachse der Waffe.
- **Texturen.** Alle eingebetteten Texturen sind höchstens 1024 × 1024 Pixel groß.

[GLB](iska.glb) · [Menüpose](vorschau_pose.png) · [Seite](vorschau_seite.png) · [Kampfansicht](vorschau_kampf.png) · [Rechte Hand](vorschau_hand.png)

Die Kampfansicht zeigt die Ausgangsstellung der Aktion Shoot von hinten oben. Geprüft wurden die exportierte Struktur und die Blender-Vorschauen. Der Vergleich mit der anderen Fassung in Godot steht aus.
