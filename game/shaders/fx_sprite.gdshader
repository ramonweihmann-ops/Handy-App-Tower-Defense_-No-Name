shader_type spatial;
// Bildfolge (Sprite-Sheet) als Billboard zur Kamera. Gerichtete Effekte (Mündung, Geschoss, Strahl) drehen sich
// auf dem Bildschirm so, dass ihre Oberkante (im Bild „nach oben“) in Richtung dir zeigt, und lassen sich entlang
// dieser Richtung strecken (Strahl zwischen Held und Ziel). Ein Material je Bildfolge, alles Wechselnde als
// Instanzwert, damit viele gleichzeitige Effekte dasselbe Material teilen.
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, skip_vertex_transform, blend_mix;

uniform sampler2D tex : source_color, filter_linear, repeat_disable;
uniform vec2 grid = vec2(4.0, 4.0);      // Spalten, Zeilen
uniform vec2 anchor = vec2(0.5, 0.5);    // Ursprung im Einzelbild (0..1, y nach unten)
uniform float inset = 0.004;             // gegen Ausbluten der Nachbarbilder

instance uniform float frame = 0.0;
instance uniform vec2 size = vec2(1.0, 1.0);   // Breite, Länge (Weltmaß)
instance uniform vec3 dir = vec3(0.0);          // Weltrichtung; 0 = nicht drehen
instance uniform float alpha = 1.0;
instance uniform float stretch = 0.0;           // 1 = Strahl: Länge um die Verkürzung in die Tiefe kürzen

void vertex() {
	vec2 q = VERTEX.xy;                                   // −0,5 … 0,5, y nach oben
	q -= vec2(anchor.x - 0.5, 0.5 - anchor.y);
	q *= size;
	vec3 center = (MODELVIEW_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 dv = (VIEW_MATRIX * vec4(dir, 0.0)).xyz;
	vec2 d = dv.xy;
	if (stretch > 0.5 && length(dv) > 0.0001) {
		// Ein Strahl, der in die Tiefe zeigt, erscheint auf dem Bildschirm kürzer: nur der Anteil quer zur Blickrichtung
		q.y *= length(dv.xy) / length(dv);
	}
	if (length(d) > 0.0001) {
		d = normalize(d);
		// +y des Bildes auf d drehen
		q = vec2(q.x * d.y + q.y * d.x, -q.x * d.x + q.y * d.y);
	}
	VERTEX = center + vec3(q, 0.0);
	NORMAL = vec3(0.0, 0.0, 1.0);
}

void fragment() {
	float f = floor(frame + 0.5);
	vec2 cell = vec2(mod(f, grid.x), floor(f / grid.x));
	vec2 uv = clamp(UV, vec2(inset), vec2(1.0 - inset));
	vec4 c = texture(tex, (cell + uv) / grid);
	ALBEDO = c.rgb;
	ALPHA = c.a * alpha;
}
