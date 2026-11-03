# Icons und Logos: Vorgaben für neue Symbole (Stand 03.11.2026)

Übersicht aller heutigen Symbole: Arbeitsfläche „Menü-Entwürfe Wurmloch“, Reihe „Icons und Logos“.
So kann jedes Symbol überall gleich sauber eingesetzt werden (Kopfleiste 20 px bis Belohnungsfenster 120 px).

## Stil

- Space-Comic wie der Hauptbildschirm v4: plastisch, kräftige Farben, weiche Lichtkante oben links, dunkle Umrisslinie (etwa 3 % der Bildbreite). Kein Fotorealismus.
- Gleiche Perspektive für alle: leicht von oben vorn (etwa 15°), Licht von oben links.
- Muss bei 20 × 20 Pixeln noch erkennbar sein: klare Silhouette, wenige Details.
- Nicht ins Bild: Schrift, Zahlen, Hintergrund, Kachel oder Rahmen, rote Hinweispunkte, Leuchten oder Schatten nach außen. Das alles zeichnet das Spiel.

## Dateiformat (für jedes Symbol)

- PNG, 32 Bit mit echter Transparenz, Farbraum sRGB.
- 512 × 512 Pixel, quadratisch. Motiv mittig, rundum 32 Pixel frei (Motiv höchstens 448 Pixel).
- Stehende Dinge (Truhen, Gebäude-Symbole): Standfläche unten bei etwa 470 Pixeln, damit alle gleich auf der Linie stehen.
- Ein Symbol pro Datei, Dateinamen wie unten. Bitte nicht als Sammelbild mit mehreren Symbolen.

## Animation

- Ihr liefert nur Standbilder. Glanzstreifen, Wippen, Pulsieren und das Einsammeln in die Kopfleiste baut das Spiel selbst.
- Nur für Gold, Edelsteine, Energie und Talent-Stern zusätzlich eine echte Drehung: 12 Bilder je 256 × 256 auf einem Bogen 1024 × 768 (4 Spalten × 3 Reihen), Bild 1 = Vorderseite, gleichmäßig 30° pro Bild, nahtlose Schleife. Dateiname z. B. spin_gold.png.
- Truhen (später): 3 Standbilder an derselben Stelle: zu, halb offen, offen mit Licht. Dateinamen chest_gold_0.png, _1, _2.

## 3D-Modelle

- Für Symbole keine 3D-Modelle nötig. Viele 3D-Symbole gleichzeitig kosten auf dem Handy zu viel Leistung, und ich würde sie ohnehin zu Bildern rendern.
- Falls ChatGPT lieber in 3D baut: GLB, höchstens 2.000 Dreiecke, eine Textur bis 512 × 512, Ursprung in der Mitte, Y oben, Vorderseite +Z, Animation „Spin“ (1,2 s, eine Umdrehung um Y). Daraus rendere ich die Bilder und Drehbögen selbst.

## Benötigte Dateien

- Währungen: icon_gold, icon_gems, icon_energy, icon_stars, icon_pass, icon_cards, icon_trophy, icon_league, icon_medal
- Truhen: chest_wood, chest_iron, chest_silver, chest_gold, chest_epic
- Booster: booster_luftangriff, booster_medipack, booster_zeitlupe, booster_kuppel, booster_munition
- Kampf: icon_core (Energiekern), icon_shield, icon_skull, icon_clock, icon_crown
- Aktionen: act_daily, act_wheel, act_missions, act_shop, act_modes und Reiter nav_shop, nav_heroes, nav_battle, nav_upgrades, nav_base (gibt es schon im Hauptbildschirm v4, bitte einzeln freigestellt).
- Champion-Rundbilder: haben wir aus den 2D-Designs. Neu nur bei Stilwechsel: 512 × 512, Kopf und Schultern, Augen bei etwa 40 % der Höhe, transparenter Hintergrund (Ring und Farbverlauf macht das Spiel).
- Ablage im Repository: Vorlage_Raw/Icons_v1/ mit einer kurzen LIESMICH.md (Liste, Quelle, Lizenz).
