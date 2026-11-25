# Vier Bosse neu entwerfen – Auftrag für ChatGPT (Stand 25.11.2026)

**Kosten: keine.** Nur die eingebaute Bildgenerierung im bestehenden Konto.

Befund: Beim Monster-Redesign (Planeten 2–15) gefallen dem Nutzer vier Bosse noch nicht:

- **Kristallriese** (Welt 10, Herz des Wurmlochs): komplett neu erfinden.
- **Fabrikmutter** (Welt 20, Robo-Fabrik): Die Monster passen, der Boss ist zu schlicht.
- **Schrottkoloss** (Welt 19, Schrotthalden): sieht aus wie Klötze mit gelben Kugeln, braucht viel mehr Detail.
- **Pilzriese** (Welt 24, Sporennebel): Die Pilze sollen echt aussehen und am Körper wachsen, nicht nur weiße
  Punkte sein. Die Körperform (Gorilla-Riese) gibt es schon und soll neu werden.

Jedes Referenzblatt zeigt den aktuellen Stand (vorn schräg, Seite, hinten, Angriff, im Spiel) und unten rechts
die Monster der Welt als Stilvorlage. Die Blätter liegen in `Bosse_Neu_Referenz/`.

Ablauf: Die Prompts einzeln abschicken. ChatGPT schlägt je drei Konzepte vor und zeichnet das stärkste. Die
Entwürfe, die dem Nutzer gefallen, baut Claude in Blender nach (`tools/monster/monster_aufsatz.py`). Werte und
Skelett bleiben gleich, und vor dem Einbau gibt es ein Mockup. Kann ChatGPT einen Link nicht öffnen, das Blatt
herunterladen und an die Nachricht anhängen.

Direkte Bildlinks:

- Kristallriese: https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/kristallriese.png
- Fabrikmutter: https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/fabrikmutter.png
- Schrottkoloss: https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/schrottkoloss.png
- Pilzriese: https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/pilzriese.png

---

## B1: Kristallriese

~~~~text
Referenzblatt „Kristallriese“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/kristallriese.png

Oben siehst du den aktuellen Boss. Er gefällt mir nicht. Unten rechts stehen die drei Monster seiner Welt „Herz des Wurmlochs“ (Sternenflatterer, Leerenwandler, Sternenpanzer) als Stilvorlage.

Aufgabe: Erfinde den Boss „Kristallriese“ komplett neu. Wandle den aktuellen nicht nur ab. Schlage zuerst 3 unterschiedliche Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Thema: Ein Riese, der aus dem Wurmloch kommt. Seine Kristalle bestehen aus Sternenlicht und Leere statt aus Edelsteinen: dunkles, kosmisches Material, Sternenglitzern, violett-magentafarbenes Leuchten wie bei den Monstern der Welt. Er muss sich klar unterscheiden von rosa Kristallhöhlen-Monstern, von einem Golem aus Gold und Rubinen und von einem Felsgolem aus gestapelten Blöcken.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Zweibeiner mit 2 Armen und 2 Beinen. Er läuft langsam. Beim Angriff reißt er beide Fäuste hoch und schlägt zu.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile.
- Detailliertes, realistisches Maul: Zahnfleisch, einzelne, unterschiedlich große Zähne, Zunge, dunkler Rachen. Keine groben Formen.
- Bedrohlich, aber nicht blutig oder eklig.
- Im Spiel ist er klein und schräg von oben vorn zu sehen. Er braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell wie die Monster auf dem Blatt, mit kräftigen Formen, echter Oberflächenstruktur und weichem Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganzer Körper in neutraler A-Pose, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Kopf und Maul plus die Angriffspose.
~~~~

## B2: Fabrikmutter

~~~~text
Referenzblatt „Fabrikmutter“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/fabrikmutter.png

Oben siehst du den aktuellen Boss. Er gefällt mir nicht: zu schlicht, zu glatt, zu harmlos. Unten rechts stehen die drei Monster seiner Welt „Robo-Fabrik“ (Federbot, Drohnenflügler, Panzerroboter). Die Monster gefallen mir, und der Boss soll klar zu ihnen gehören.

Aufgabe: Entwirf die „Fabrikmutter“ neu. Schlage zuerst 3 Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Thema: Die Mutter-Maschine der Robo-Fabrik, aus der die Federbots kommen. Im Spiel setzt sie kleine Federbots ab. Denk an Hochofen, Presse, Fließband, Kessel oder Kran. Sie braucht viel Detail: Panzerplatten, Nieten, Schweißnähte, Rohre, Kolben, Manometer, gelb-schwarze Warnstreifen, Kratzer, Öl und Ruß, eine glühende Ofenklappe. Farben wie bei den Monstern: dunkler Stahl, Gelb als Akzent, rot glühende Augen, Schornsteine.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Keine Beine: Der Körper bewegt sich als Ganzes. Er schwankt, federt, staucht sich leicht und rollt oder gleitet langsam vorwärts. Räder, Ketten, Rollen oder ein Sockel sind erlaubt.
- Greifarme sind erlaubt, sitzen aber fest am Körper und bewegen sich nicht einzeln.
- Breite, schwere, kompakte Form.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile.
- Detailliertes Maul: ein mechanischer Kiefer aus vielen Einzelteilen (Stahlzähne, Kolben, Gitter), dahinter ein glühender Schlund. Keine groben Formen.
- Bedrohlich, aber nicht blutig oder eklig.
- Im Spiel ist sie klein und schräg von oben vorn zu sehen. Sie braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell wie die Monster auf dem Blatt, mit kräftigen Formen, echter Oberflächenstruktur und weichem Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganze Figur, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Gesicht und Maul plus der Moment, in dem sie einen Federbot absetzt.
~~~~

## B3: Schrottkoloss

~~~~text
Referenzblatt „Schrottkoloss“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/schrottkoloss.png

Oben siehst du den aktuellen Boss. Er sieht aus wie Spielzeug aus Klötzen und gelben Kugeln und hat viel zu wenig Detail. Unten rechts stehen die drei Monster seiner Welt „Schrotthalden“ (Schrottwicht, Rostschlurfer, Schrottbrecher) als Stilvorlage.

Aufgabe: Entwirf den „Schrottkoloss“ neu und mit deutlich mehr Detail. Schlage zuerst 3 Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Thema: Ein Riese, den sich die Schrotthalde selbst zusammengebaut hat. Er besteht aus erkennbaren Schrottteilen statt aus Klötzen: Autotüren und Motorhauben als Panzerplatten, Radkappen, Ketten, verbogene Rohre und Bewehrungsstahl, Ölfässer, Federn, Zahnräder, ein Motorblock als glühendes Herz, eine Baggerschaufel oder ein Kranhaken als Faust. Dazu Rost in vielen Tönen, abblätternder Lack, Beulen, Schweißnähte und Schrauben. Gelb-schwarze Warnstreifen wie beim Schrottbrecher und rot glühende Augen wie bei allen Monstern dieser Welt.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Zweibeiner mit 2 Armen und 2 Beinen, schwer und leicht gebückt. Er läuft langsam. Beim Angriff reißt er beide Fäuste hoch und schlägt zu.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile.
- Detailliertes Maul: ein Kiefer aus Metall (z. B. Kühlergrill oder Baggerschaufel) mit vielen einzelnen, verschieden geformten Stahlzähnen, dahinter ein glühender Schlund. Keine groben Formen.
- Bedrohlich, aber nicht blutig oder eklig.
- Im Spiel ist er klein und schräg von oben vorn zu sehen. Er braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell wie die Monster auf dem Blatt, mit kräftigen Formen, echter Oberflächenstruktur und weichem Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganzer Körper in neutraler A-Pose, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Kopf und Maul plus die Angriffspose.
~~~~

## B4: Pilzriese

~~~~text
Referenzblatt „Pilzriese“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/pilzriese.png

Oben siehst du den aktuellen Boss, unten rechts die drei Monster seiner Welt „Sporennebel“ (Sporenwicht, Myzelwandler, Schwammbrecher) als Stilvorlage.

Was mir nicht gefällt: Die Pilze wirken aufgeklebt und sind kaum mehr als weiße Punkte. Außerdem gibt es die Körperform, einen breitschultrigen Gorilla-Riesen, bei meinen anderen Bossen schon.

Aufgabe: Erfinde für den „Pilzriesen“ eine neue Körperform. Schlage zuerst 3 Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Form: weiterhin 2 Arme und 2 Beine, aber klar anders als ein breitschultriger Gorilla-Riese. Anregungen: hoch und hager auf langen Beinen, gebückt unter einem riesigen Pilzhut, der Kopf und Rücken bildet, oder ein wandelnder Stumpf voller Pilze. Er soll sich auch von einer Pilzkönigin (Boss der Nachbarwelt) und von einem Baumriesen aus Ästen und Blättern unterscheiden.

Pilze: Sie wachsen wirklich aus dem Körper heraus, sitzen dicht an und brechen aus Rissen in der Haut. Mit echtem Pilz-Detail: Hüte mit Lamellen auf der Unterseite, Stiele mit Manschette, Konsolenpilze (Baumschwämme) als Stufen an Schultern und Rücken, Morcheln, Boviste, kleine Büschel, feines Myzel-Geflecht, Sporenstaub. Unterschiedliche Größen und Arten, natürliche Farben und Flecken, keine bloßen weißen Punkte. Farben passend zu den Monstern auf dem Blatt.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Er läuft langsam. Beim Angriff reißt er beide Arme hoch und schlägt zu.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile.
- Detailliertes, realistisches Maul: Zahnfleisch, einzelne, unterschiedlich große Zähne, Zunge, dunkler Rachen. Keine groben Formen.
- Bedrohlich, aber nicht blutig oder eklig.
- Im Spiel ist er klein und schräg von oben vorn zu sehen. Er braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell wie die Monster auf dem Blatt, mit kräftigen Formen, echter Oberflächenstruktur und weichem Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganzer Körper in neutraler A-Pose, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Kopf und Maul plus die Angriffspose.
~~~~

## B5: Edelsteingolem (Kommentar 25.11.2026)

Dem Nutzer gefallen beim aktuellen Edelsteingolem (Welt 16, Glitzerschlucht) nicht: die Farben, die Kristallformen,
die Krone, die Augen und das Maul. Blatt: `Bosse_Neu_Referenz/edelsteingolem.png`.

~~~~text
Referenzblatt „Edelsteingolem“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/edelsteingolem.png

Oben siehst du den aktuellen Boss der Welt „Glitzerschlucht“, unten rechts die Monster dieser Welt (Glitzerwicht, Facettenfalter, Goldbrecher) als Stilvorlage. Mir gefallen am aktuellen Boss nicht: die Farben, die Kristallformen, die Krone, die Augen und das Maul.

Aufgabe: Entwirf den „Edelsteingolem“ neu. Schlage zuerst 3 unterschiedliche Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Thema: Ein mächtiger Golem aus einer Schatzhöhle voller Edelsteine – Gold, geschliffene Edelsteine und polierter Stein. Finde eine eigene, edle Farbwelt (z. B. warmes Gold mit tiefem Smaragd, Saphir oder Amethyst) statt Gold mit knalligem Rot. Edelsteine in klaren, schön geschliffenen Formen (Brillant-, Smaragd- oder Tropfenschliff), in Fassungen eingelassen – keine zufälligen spitzen Splitter, keine eckigen Low-Poly-Brocken. Er muss sich klar unterscheiden von einem violetten Sternen-Riesen und von rosa Kristallhöhlen-Monstern.

Gesicht: ausdrucksstarke, böse leuchtende Augen mit schweren Brauen (keine leeren weißen Kugeln). Maul im Comic-Stil, das zum Golem passt (z. B. ein Mund aus Stein mit Goldkante und eingesetzten Edelsteinzähnen) – nicht weit aufgerissen und nicht wie ein echtes Gebiss.

Krone: neu gestalten, fest auf dem Kopf (oder mit ihm verwachsen), mit wenigen großen gefassten Steinen – nichts schwebt, keine dünnen Zacken.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Zweibeiner mit 2 Armen und 2 Beinen, kräftige Hände mit Daumen und vier Fingern. Er läuft langsam. Beim Angriff reißt er beide Fäuste hoch und schlägt zu.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile.
- Bedrohlich, aber im freundlichen Comic-Stil, nicht blutig oder eklig.
- Im Spiel ist er klein und schräg von oben vorn zu sehen. Er braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell mit großen, ruhigen Formen und runden Kanten (wenig Kleinteile), weiches Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganzer Körper in neutraler A-Pose, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Kopf und Maul plus die Angriffspose.
~~~~

## B6: Magma-Golem (Kommentar 25.11.2026)

Der Magma-Golem (Welt 4, Lava-Kolonie) soll komplett neu entworfen werden. Blatt: `Bosse_Neu_Referenz/magmagolem.png`.

~~~~text
Referenzblatt „Magma-Golem“ aus meinem 3D-Tower-Defense-Spiel fürs Handy, bitte öffnen und genau ansehen:
https://raw.githubusercontent.com/ramonweihmann-ops/Handy-App-Tower-Defense_-No-Name/claude/amazing-hypatia-yl59v4/Vorlage_Raw/Bosse_Neu_Referenz/magmagolem.png

Oben siehst du den aktuellen Boss der Welt „Lava-Kolonie“, unten rechts die Monster dieser Welt (Glutwicht, Schlackenwandler, Magmabrecher) als Stilvorlage. Der aktuelle Boss gefällt mir nicht: Er wirkt wie ein Haufen eckiger Felsbrocken mit gelben Kugeln, ohne Charakter.

Aufgabe: Entwirf den „Magma-Golem“ komplett neu. Schlage zuerst 3 unterschiedliche Konzepte in je 2 Sätzen vor und zeichne dann das stärkste.

Thema: Ein Riese aus dem Inneren eines Vulkans. Dunkles, erkaltetes Lavagestein (Basalt, Schlacke) mit glühenden Rissen, aus denen Magma leuchtet; ein glühender Kern in der Brust; heiße Lavaströme, die über Schultern und Arme laufen und erstarren; Rauch und Glut nur als feste Formen am Körper. Farben passend zu den Monstern: fast schwarzes Gestein, glühendes Orange und Gelb, etwas tiefes Rot. Er muss sich klar unterscheiden von einem Schrott-Roboter, einem violetten Sternen-Riesen und einem Golem aus Gold und Edelsteinen – und darf kein Stapel aus eckigen Low-Poly-Blöcken sein.

Gesicht: gut lesbares, böses Gesicht mit glühenden Augen unter schweren Gesteinsbrauen. Maul im Comic-Stil, das zum Lavawesen passt (z. B. ein halb geöffnetes Maul mit Gesteinslippen, in dem Magma glüht, und ein paar kantigen Basaltzähnen) – nicht weit aufgerissen und nicht wie ein echtes Gebiss.

Bau (muss so bleiben, die Figur wird in Blender nachgebaut und auf ein vorhandenes Skelett gesetzt):
- Zweibeiner mit 2 Armen und 2 Beinen, große Hände mit Daumen und vier Fingern. Er läuft langsam. Beim Angriff reißt er beide Fäuste hoch und schlägt zu.
- Alles sitzt fest am Körper: Nichts schwebt, keine dünnen, weit abstehenden Teile, keine losen Funken oder Rauchwolken.
- Bedrohlich, aber im freundlichen Comic-Stil, nicht blutig oder eklig.
- Im Spiel ist er klein und schräg von oben vorn zu sehen. Er braucht eine klare Silhouette, ein gut lesbares Gesicht und 2–3 Hauptfarben plus einen Leuchtakzent.
- Eigenständiges Design, keine bekannte Figur aus Spielen oder Filmen.

Stil: stilisiertes 3D-Spielmodell mit großen, ruhigen Formen und runden Kanten (wenig Kleinteile), deutliche Oberflächenstruktur, weiches Studiolicht.

Ausgabe: Bild 1 ist ein Charakter-Turnaround: vorn, schräg vorn, Seite, hinten. Ganzer Körper in neutraler A-Pose, einfarbig grauer Hintergrund, kein Text. Danach Bild 2: Nahaufnahme von Kopf und Maul plus die Angriffspose.
~~~~
