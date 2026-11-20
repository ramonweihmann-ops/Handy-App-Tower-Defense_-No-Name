# Wöchentliches Event (seit 0.10.38)

Wunsch des Nutzers (19.11.2026): ein wöchentliches Event mit eigener Belohnungsleiste, damit es etwas Rotierendes
gibt. Mockup „Shop · Event“ (Shop-Event-Neu.dc.html), freigegeben am 20.11.2026. Im Spiel im Shop, Reiter „Event“.

## Ablauf

- Jede Woche (Montag 0 Uhr UTC) beginnt ein neues Event: Punkte und abgeholte Stufen fangen bei null an.
- Themen reihum (`MetaData.EVENT_THEMES`); jedes hat eine eigene Fassung des Banners (Farben, Boss, Texte):

| Thema | zählt als Thema-Gegner | Boss im Banner |
|---|---|---|
| Schleimflut | Schleimlinge und Schleimmütter | Schleimmutter |
| Frostwoche | alle Gegner, die beim Besiegen verlangsamt sind (Kalles Frost, Zeitlupe, Novas Feld, Schwerefeld) | Frost-Schleimmutter |
| Zombienacht | Krabbler, Zombies, Brecher, Kolosse | Zombie-Koloss |
| Lavawoche | starke Gegner (Panzerkäfer, Brecher, Krabbenpanzer …) | Lava-Koloss |

- Event-Punkte (`MetaData.EVENT_POINTS`): gewonnenes Level +20, Thema-Gegner +1, Boss +50, Tagesmission abgeholt
  +30. Nur im Abenteuer, nicht im Multiplayer und nicht in Tests.
- Belohnungsleiste: zehn Stufen zu je 100 Punkten (`MetaData.EVENT_REWARDS`): 300 Gold, 10 Edelsteine, 5 Heldenkarten,
  1 Stern, Silbertruhe, 600 Gold, 20 Edelsteine, 10 Heldenkarten, 2 Sterne, Event-Truhe (Goldtruhe). Truhen geben
  Booster-Teile wie im Shop.
- Erreichte Stufen holt man durch Antippen der Karte („Holen“). Roter Punkt am Reiter „Event“ und am Shop in der
  unteren Leiste, solange eine Stufe bereitliegt.

## Technik

- Spielstand: `Save.event()` ({week, points, claimed}), `event_add`, `event_stage`, `event_state`, `event_ready`,
  `event_claim`.
- Seite: `ui_mock/shop_event` aus `tools/mock2game/cfg/shop_event.json` (eine Fassung je Thema, `shop_event.js`);
  Restzeit, Punkte, Balken und die Karten zeichnet `tab_shop.gd` (`EventCard`, `EventBar`). Der Shop-Rahmen
  (`cfg/shop.json`) zeigt beim Reiter Event nur noch den Rahmen.
- Prüfung: `--eventcheck` (in `scripts/test.sh`): Wochenwechsel, Themen, Zählung, Stufen, Abholen, Truhen.
- Offen: Werte im Labor abstimmen (bei fünf Leveln am Tag sind 1.000 Punkte schon nach wenigen Tagen erreicht).
