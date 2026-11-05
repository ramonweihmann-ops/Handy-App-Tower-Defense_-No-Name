# Acht fehlende Shop-Symbole

## Freigegebene Anpassung vom 5. November 2026

`icon_werbefrei.png` enthält die bestätigte, etwas ernsthaftere Variante: schlankerer Rahmen mit klaren gefasten Kanten, kompakte Bedienelemente und zurückhaltender Glanz. Violettblauer Bildschirm, Abspiel-Dreieck und rotes Verbotszeichen bleiben erhalten. Die Übersicht zeigt bereits diese neue Fassung. Die übrigen sieben Symbole bleiben in ihrer freigegebenen Form. Die zusätzliche Bildanweisung steht unter „Korrektur“ in `BILDANWEISUNG.txt`.

Nur die acht angeforderten Symbole ergänzen. Vorhandene Münz-/Edelstein-Stapel, Truhe, Uhr, Booster, Shop-Seiten, Preise und Knöpfe bleiben unverändert. Die Bilder enthalten keine Preise oder Texte; einzige Ausnahme ist `×2` im Tempo-Symbol.

| Datei | Motiv | Größe | Einsatz im bestehenden Shop |
|---|---|---|---|
| icon_geldsack.png | Brauner Geldsack mit hervorquellenden Goldmünzen | 512 × 512 | Gold-Shop, 15.000 Gold |
| icon_goldschatz.png | Offene Truhe voller Goldmünzen | 512 × 512 | Gold-Shop, 40.000 Gold |
| icon_diamantensack.png | Violettblauer Beutel voller rosa Edelsteine | 512 × 512 | Edelstein-Shop, 2.600 Edelsteine |
| icon_edelsteintruhe.png | Offene Truhe voller rosa Edelsteine | 512 × 512 | Edelstein-Shop, 5.500 Edelsteine |
| icon_tempo_x2.png | Türkise Stoppuhr, grünes ×2-Schild und Vorspul-Pfeile | 512 × 512 | 2× Tempo |
| icon_werbefrei.png | Bildschirm mit Abspiel-Dreieck und rotem Verbotszeichen | 512 × 512 | Werbefrei und Werbefrei Plus |
| icon_booster_silbertruhe.png | Silber-/Stahltruhe mit blauen Akzenten, Raketen und Medipack | 512 × 512 | Booster-Truhen, Silbertruhe |
| icon_booster_goldtruhe.png | Dieselbe Truhenform in Gold mit violetten Akzenten und denselben Boostern | 512 × 512 | Booster-Truhen, Goldtruhe |

Alle acht Dateien sind PNG, RGBA mit echter Transparenz und geradem Alpha, Farbraum sRGB. Das Motiv liegt mittig mit ungefähr 8 % freiem Außenrand. Bei 50–90 logischen Punkten Breite einsetzen; das Seitenverhältnis beibehalten und keine zusätzliche Hintergrundkachel oder Schattenfläche mit skalieren.

`uebersicht.png` zeigt alle acht Motive in einer Reihe auf `#2a1f63`. Der violette Grund und die Dateibeschriftungen gehören nur zur Übersicht und sind nicht in den einzelnen Symbolen enthalten.

Form- und Farbvorlage: `Vorlage_Raw/Shop_Bilder_Referenz/symbole_vorhanden.png`. Die vorhandene Goldmünze hat einen geprägten abgerundeten Stern und einen Innenring; die vorhandenen Edelsteine sind breit facettiert und rosa. Raketen und Medipack folgen ebenfalls dieser Vorlage, einschließlich rotem Herz auf dem Medipack. Die drei Shop-Entwürfe dienten nur zur Kontrolle des Einsatzortes; sie wurden nicht geändert.

Die acht Symbole wurden einzeln mit der eingebauten Bildgenerierung im bestehenden Konto erstellt und technisch auf 512 × 512 gebracht. Keine weiteren kostenpflichtigen Dienste verwendet. Die tatsächlich verwendeten Bildanweisungen stehen in `BILDANWEISUNG.txt`.

PNG-Größen, Transparenz und Außenränder wurden geprüft. Die endgültige Wirkung in den Shop-Karten prüft Claude nach dem Einsetzen ins Mockup. Keine Änderungen am Spielcode oder an Shop-Layouts in diesem Paket.
