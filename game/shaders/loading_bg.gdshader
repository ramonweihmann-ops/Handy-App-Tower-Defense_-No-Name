shader_type canvas_item;
// Hintergrund des Ladebildschirms: Weltraum mit Nebel, funkelnden Sternen und einem
// drehenden Wurmloch-Wirbel um den Planeten (Vorlage: Mockup „Ladebildschirm · animiert“).

uniform vec2 size_px = vec2(720.0, 1280.0);   // Größe der Fläche in Pixeln
uniform vec2 center_px = vec2(360.0, 560.0);  // Mitte des Wirbels (Planet)
uniform float radius_px = 200.0;              // Radius des Planeten

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float ring(float r, float at, float width) {
	return smoothstep(width, 0.0, abs(r - at));
}

void fragment() {
	vec2 px = UV * size_px;
	float y = UV.y;
	// Verlauf von Tiefblau über Blau zu Violett, unten wieder dunkel
	vec3 col = mix(vec3(0.02, 0.03, 0.15), vec3(0.08, 0.09, 0.35), smoothstep(0.0, 0.45, y));
	col = mix(col, vec3(0.23, 0.12, 0.43), smoothstep(0.45, 0.72, y));
	col = mix(col, vec3(0.10, 0.06, 0.23), smoothstep(0.72, 1.0, y));
	float u = size_px.x / 390.0;
	// Nebel: cyan oben rechts, rosa-violett in der Mitte
	col += vec3(0.31, 0.86, 1.0) * 0.2 * smoothstep(1.0, 0.0, length((px - vec2(330.0, 70.0) * u) / (vec2(150.0, 130.0) * u)));
	vec2 q = (px - vec2(195.0, 500.0) * u) / (vec2(260.0, 120.0) * u);
	q = vec2(q.x * 0.97 - q.y * 0.24, q.x * 0.24 + q.y * 0.97);
	col += mix(vec3(1.0, 0.47, 0.75), vec3(0.59, 0.31, 1.0), 0.5) * 0.22 * smoothstep(1.0, 0.0, length(q));
	// Sterne in zwei Größen, funkeln unterschiedlich schnell
	for (int i = 0; i < 2; i++) {
		float sc = i == 0 ? 0.11 : 0.06;
		vec2 g = px / u * sc;
		vec2 cell = floor(g);
		float h = hash(cell + float(i) * 17.0);
		float d = length(fract(g) - 0.5 - (vec2(hash(cell + 3.1), hash(cell + 7.7)) - 0.5) * 0.6);
		float star = step(0.93, h) * smoothstep(0.16, 0.0, d);
		col += vec3(0.95, 0.96, 1.0) * star * (0.45 + 0.55 * sin(TIME * (1.0 + h * 3.0) + h * 40.0));
	}
	// Wurmloch-Wirbel um den Planeten: farbige Schlieren, die sich langsam drehen
	vec2 p = px - center_px;
	float r = length(p) / radius_px;
	float a = atan(p.y, p.x);
	float band = smoothstep(1.05, 1.25, r) * smoothstep(1.75, 1.35, r);
	float sw = 0.5 + 0.5 * sin(a * 3.0 - TIME * 0.7 + r * 4.0);
	vec3 swirl = mix(vec3(0.47, 0.78, 1.0), vec3(0.75, 0.55, 1.0), sw);
	swirl = mix(swirl, vec3(1.0, 0.59, 0.82), 0.5 + 0.5 * sin(a * 2.0 + TIME * 0.4));
	col += swirl * band * (0.15 + 0.35 * sw);
	// leuchtende Ringe: einer atmet, zwei laufen nach außen
	col += vec3(0.62, 0.83, 1.0) * ring(r, 1.27 + 0.08 * sin(TIME * 2.1), 0.012) * 0.5;
	for (int k = 0; k < 2; k++) {
		float ph = fract(TIME / 3.2 + float(k) * 0.5);
		col += mix(vec3(0.75, 0.89, 1.0), vec3(0.82, 0.66, 1.0), float(k)) * ring(r, 0.85 + ph * 1.2, 0.02) * (1.0 - ph) * 0.6;
	}
	col += vec3(0.75, 0.89, 1.0) * smoothstep(1.6, 0.7, r) * 0.1 * (0.6 + 0.4 * sin(TIME * 2.6));
	COLOR = vec4(col, 1.0);
}
