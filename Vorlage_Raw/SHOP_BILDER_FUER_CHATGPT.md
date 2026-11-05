# Shop-Symbole: Auftrag für ChatGPT (Stand 05.11.2026)

Zum Kopieren in ChatGPT. Dazu als Bilder anhängen (alle in `Vorlage_Raw/Shop_Bilder_Referenz/`):
- `symbole_vorhanden.png`: unsere bisherigen Symbole, an deren Stil sich alles richten soll
- `shop_entwurf_Angebote.jpg`, `shop_entwurf_Truhen.jpg`, `shop_entwurf_Aufladen.jpg`: der neue Shop, in dem die Symbole sitzen

---

Ich entwickle ein Handy-Tower-Defense-Spiel (hochkant, Comic-Stil im Weltraum, Godot). Der Shop ist fertig gestaltet
(Entwürfe angehängt). Es fehlen nur noch **acht Symbole**. Alles andere (Münzen, Edelsteine, Truhe, Uhr, Booster)
gibt es schon. Bitte nur diese acht Symbole erstellen, nichts weiter.

**Stil (wie `symbole_vorhanden.png`):** weiche, glänzende Comic-Schattierung, kräftige Farben, Licht von links oben,
leichte Ansicht von schräg oben, kein Fotorealismus, keine dicke schwarze Kontur. Unsere Goldmünze und unser rosa
Edelstein sollen in den Symbolen genau so aussehen wie in der Vorlage (gleiche Form und Farbe), damit alles zusammenpasst.
Keine Schrift auf den Symbolen (einzige Ausnahme: „×2“ beim Tempo), keine Logos, nichts von anderen Spielen nachmachen.

**Die acht Symbole:**

| Datei | Motiv | Wo im Shop |
|---|---|---|
| `icon_geldsack.png` | prall gefüllter Geldsack aus braunem Stoff, oben zugebunden, Goldmünzen quellen heraus, ein paar liegen davor | Gold-Shop, 15.000 Gold |
| `icon_goldschatz.png` | offene Schatztruhe randvoll mit Goldmünzen, Münzen fallen über den Rand | Gold-Shop, 40.000 Gold |
| `icon_diamantensack.png` | prall gefüllter Beutel (violett oder blau) mit rosa Edelsteinen, oben offen, Edelsteine schauen heraus | Edelstein-Shop, 2.600 Edelsteine |
| `icon_edelsteintruhe.png` | offene Truhe randvoll mit rosa Edelsteinen, leicht leuchtend | Edelstein-Shop, 5.500 Edelsteine |
| `icon_tempo_x2.png` | runde Stoppuhr (türkis wie unsere Uhr) mit großem grünem „×2“-Schild davor, zwei Vorspul-Pfeile als Bewegung | 2× Tempo |
| `icon_werbefrei.png` | kleiner Bildschirm mit Abspiel-Dreieck (Werbevideo), darüber ein rotes Verbotszeichen (Kreis mit Schrägstrich), freundlich, nicht bedrohlich | Werbefrei, Werbefrei Plus |
| `icon_booster_silbertruhe.png` | Truhe aus Silber und Stahl mit blauen Akzenten, daneben klein unsere Booster (Raketen vom Luftangriff, Medipack) | Booster-Truhen, Silbertruhe |
| `icon_booster_goldtruhe.png` | dieselbe Truhe in Gold mit violetten Edelstein-Akzenten, leichtes Leuchten, daneben dieselben Booster | Booster-Truhen, Goldtruhe |

**Technik:**
- Jedes Symbol einzeln als PNG mit **transparentem Hintergrund**, **512 × 512 Pixel**, Motiv mittig mit etwa 8 % Rand.
- Gut lesbar auch ganz klein (die Symbole erscheinen im Spiel mit 50–90 Punkten Breite).
- Zusätzlich `uebersicht.png`: alle acht nebeneinander auf dunkelviolettem Grund (#2a1f63), zur Kontrolle.

**Bitte liefern (Ordner `Vorlage_Raw/Shop_Bilder_v1/` auf GitHub, Branch `claude/amazing-hypatia-yl59v4`):**
1. die acht PNG-Dateien (Namen wie oben)
2. `uebersicht.png`
3. `LIESMICH_CLAUDE.md`: kurz je Datei Motiv und Größe, wo es hingehört (Tabelle oben übernehmen)
4. `BILDANWEISUNG.txt`: die verwendeten Bildprompts

Nur die eingebaute Bildgenerierung im bestehenden Konto verwenden, keine weiteren kostenpflichtigen Dienste.
