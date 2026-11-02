# Prüfung der GLB-Vorgaben (Claude, 02.11.2026)

Geprüft: `README_FUER_CLAUDE.md` und `PRODUKTIONSVORGABEN.json` gegen den Spielcode
(`game/scripts/battle/hero.gd`, `enemy.gd`, `models.gd`, `game/scripts/ui/hero_view_3d.gd`).

**Ergebnis:** Die Vorgaben passen in den Grundzügen (GLB, Y oben, 2 Einheiten, Ursprung zwischen den
Füßen, eingebettete Texturen bis 1024, Animationen ohne Vorwärtsbewegung, Lizenznachweis). Es fehlen
einige Punkte, ohne die das Spiel die Modelle nicht sauber nutzen kann, und es gibt einen inhaltlichen
Widerspruch bei drei Waffen.

## 1. Waffen: Design und Spielmechanik passen bei drei Helden nicht zusammen

Im Spiel hat jeder Held eine Waffenart mit eigener Wirkung (`GameData.HEROES`, `family`):

| Held | im Spiel | im freigegebenen Design | passt? |
|---|---|---|---|
| Dusty Jo | Revolver | Revolver | ja |
| Iska | Maschinengewehr (Dauerfeuer) | Sturmgewehr | ja |
| Brocken | Raketenwerfer (Flächenschaden) | Raketenwerfer | ja |
| Volta | **Blitzwerfer** (Kettenblitz) | Pistole + Diagnosegerät | **nein** |
| Kalle | **Eiskanone** (verlangsamt) | Pistole | **nein** |
| Käpt'n Margot | Schrotflinte | Doppelflinte | ja |
| Lynx | Präzisionsgewehr | Scharfschützengewehr | ja |
| Fritzi | **Flammenwerfer** (Kegel, Brand) | hölzerne Doppelflinte | **nein** |

**Entschieden (02.11.2026): Wirkung behalten, Waffen mechanisch.** Keine Laser, kein Plasma.
- **Volta:** Pistole mit Funkenspule am Lauf (Funkenschuss springt auf Nachbargegner) + Diagnosegerät
  in der anderen Hand. Im Spiel „Funkenpistole“.
- **Kalle:** Pistole mit Kühlzylinder unter dem Lauf, leichter Frostdampf an der Mündung (Frostmunition,
  verlangsamt). Im Spiel „Frostpistole“.
- **Fritzi:** hölzerne Doppelflinte wie im Design, mit Brandmunition (Feuerkegel, setzt in Brand).
  Im Spiel „Brandflinte“. Damit sie sich von Käpt'n Margots Flinte abhebt: Holz und Messing statt
  dunklem Metall, rote Patronenschlaufe am Schaft.

Die Effekte (Funken, Frost, Feuer) zeichnet das Spiel selbst; sie gehören nicht ins Modell.

## 2. Ergänzungen für die GLB-Dateien

**Waffe, Anker und Mündung: exakte Namen (verbindlich)**

| Objekt | exakter Name | hängt an | Zweck |
|---|---|---|---|
| Waffen-Anker | `WeaponSocket` | Knochen der rechten Hand (Bone Parent in Blender) | Griffpunkt; das Spiel kann hier auch andere Waffen anhängen |
| Waffe | `Weapon` | `WeaponSocket` | sichtbares Waffen-Mesh, starr, nicht gehäutet |
| Mündung | `Muzzle` | `Weapon` | Laufspitze; Schüsse, Mündungsfeuer, Raketen; lokale −Z-Achse zeigt in Schussrichtung |

Groß- und Kleinschreibung genau so. Ohne Leerzeichen, ohne Nummern-Endung (Blender hängt bei
Duplikaten `.001` an; das bitte vor dem Export entfernen). Das Spiel sucht nach diesen drei Namen.

**Knochennamen (verbindlich): Mixamo-Standard**, wortgetreu, mindestens:
`mixamorig:Hips`, `mixamorig:Head`, `mixamorig:RightHand`, `mixamorig:LeftHand`,
`mixamorig:RightFoot`, `mixamorig:LeftFoot`. Alle acht Helden mit demselben Skelett und denselben
Namen. Kommt das Skelett aus Meshy oder Tripo mit anderen Namen, vor dem Export auf diese Namen
umbenennen (oder über Mixamo neu riggen, das liefert sie direkt).

**Blickrichtung**
- Figur schaut in glTF-Vorwärtsrichtung (+Z), wie die bisherigen Modelle. Alle acht gleich.

**Animationen: genauer festlegen**
- `Idle`, `Run`, `Hit`: in Schleife, auf der Stelle (keine Wurzelbewegung).
- `Shoot`: beginnt im **Zielanschlag** (Waffe auf Brusthöhe nach vorn), dann Rückstoß, zurück in den
  Anschlag, **0,3–0,5 s**. Die Helden stehen im Kampf die ganze Zeit im Anschlag und spielen nur den
  Rückstoß; das Spiel pausiert dazu im Anschlag. Iska (Dauerfeuer) zusätzlich schleifenfähig.
- `Death`: endet liegend und bleibt im letzten Bild.
- **Zusätzlich für die Menüs: `Victory`** (Siegerpose, Schleife, 2–4 s). Die Heldenseiten zeigen heute
  je Held eine Pose (Jubeln, Sprung, Schuss); ohne `Victory` stehen die Helden dort nur im Idle.
- Optional `Special` (Superfähigkeit, 0,6–1,0 s).

**Dreiecke: niedriger als 15.000 ansetzen**
- Im Kampf sind bis zu 3 Helden und über 20 Gegner gleichzeitig zu sehen, auf älteren Handys mit
  einfachem Renderer. 15.000 je Held ist die Obergrenze, Ziel **8.000–12.000** je Held.
- Gegner (wenn sie neu kommen): leicht **≤ 3.000**, mittel **≤ 5.000**, stark **≤ 7.000**, Boss **≤ 12.000**.

**Materialien**
- Möglichst **ein Material und eine Textur** je Figur (Atlas), höchstens zwei (Körper, Waffe).
- Keine eigenen Lichter, Kameras oder Hilfsobjekte in der Datei (außer `Muzzle`).

## 3. Stil: großer Wechsel gegenüber dem jetzigen Spiel

Die Freigabe zeigt erwachsene, schlanke Figuren. Die Helden im Spiel sind derzeit kindlich-runde
Low-Poly-Figuren (großer Kopf). Wird umgestellt, ändern sich auch alle Heldenbilder in den Menüs und
Mockups (Heldenseiten, Karten, Rundbilder). Die rendere ich dann aus den neuen Modellen neu.
Die Figuren sind deutlich schmaler; ich prüfe nach dem ersten Modell, ob sie aus der Kampfkamera noch
gut lesbar sind, und passe bei Bedarf die Größe im Spiel an.

## 4. Lieferumfang je Held (Checkliste)

- `<id>.glb` (Namen wie in `PRODUKTIONSVORGABEN.json`)
- kurze Lizenznotiz: Werkzeug, Tarif zum Zeitpunkt der Erzeugung, Nutzungsbedingungen (Link, Datum),
  Herkunft der Animationen (z. B. Mixamo), Namensnennung falls nötig
- ein Bild von vorn und von der Seite aus Blender zur schnellen Kontrolle

## 5. Empfehlung zum Ablauf

Zuerst **nur Dusty Jo** komplett liefern. Ich baue ihn ein, teste Laufen, Drehen, Anschlag, Schuss,
Treffer, Tod, Menüpose und die Leistung, und melde die nötigen Korrekturen. Erst dann die übrigen
sieben im selben Ablauf mit denselben Einstellungen.
