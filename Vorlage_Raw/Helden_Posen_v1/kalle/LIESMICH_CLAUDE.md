# kalle · Vergleichsfassung der Champion-Posen

Tiefer seitlicher Anschlag mit Eisblaster und freier linker Hand. Die vorhandenen Daumen- und Fingerknochen sind in beiden Aktionen gekrümmt.

## Skelett und Export

Das vorhandene Rig mit Fingerknochen wurde übernommen. Die Finger sind für beide Aktionen angewinkelt.

- **Dreiecke gesamt.** 13263, einschließlich Waffe und gegebenenfalls Tablet.
- **Aktionen.** Pose als statische Menüpose und Shoot als 0,4-s-Zyklus mit Zielhaltung, kurzer Bewegung und Rückkehr auf den Startwert.
- **Koordinaten.** Ausgangsfigur 2,0 Einheiten hoch, Füße am Boden. Vorwärts in Blender ist −Y. Der GLB-Export nutzt +Y als Hochachse.
- **Waffe.** mixamorig:RightHand → WeaponSocket → Weapon → Muzzle. Der lokale −Z-Vektor des GLB-Mündungsknotens folgt der Längsachse der Waffe.
- **Texturen.** Alle eingebetteten Texturen sind höchstens 1024 × 1024 Pixel groß.

[GLB](kalle.glb) · [Menüpose](vorschau_pose.png) · [Seite](vorschau_seite.png) · [Kampfansicht](vorschau_kampf.png) · [Rechte Hand](vorschau_hand.png)

Die Kampfansicht zeigt die Ausgangsstellung der Aktion Shoot von hinten oben. Geprüft wurden die exportierte Struktur und die Blender-Vorschauen. Der Vergleich mit der anderen Fassung in Godot steht aus.
