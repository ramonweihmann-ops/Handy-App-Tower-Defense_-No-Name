shader_type spatial;
// Stationsdeck: Metallplatten mit Fugen, Nieten und Leuchtstreifen am Rand.

uniform vec3 base_col : source_color = vec3(0.2, 0.22, 0.29);
uniform vec3 line_col : source_color = vec3(0.08, 0.09, 0.13);
uniform vec3 glow_col : source_color = vec3(0.15, 0.8, 1.0);
uniform vec3 warn_col : source_color = vec3(1.0, 0.75, 0.15);
uniform vec2 tiles = vec2(4.0, 18.0);
uniform float fence_v = 0.82; // Lage des Zauns in UV.y

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 uv = UV * tiles;
	vec2 cell = floor(uv);
	vec2 f = fract(uv);
	vec2 g = abs(f - 0.5);
	float seam = smoothstep(0.46, 0.5, max(g.x, g.y));
	float n = hash(cell);
	vec3 col = base_col * (0.82 + 0.3 * n);
	// feine Riffelung
	col *= 0.94 + 0.06 * step(0.5, fract((f.x + f.y) * 6.0));
	// Nieten in den Ecken
	vec2 c = abs(f - 0.5) - 0.38;
	float rivet = smoothstep(0.045, 0.02, length(max(c, 0.0)) + 0.0 * n);
	col = mix(col, base_col * 1.6, rivet * step(0.0, min(c.x, c.y)));
	col = mix(col, line_col, seam);
	// Leuchtstreifen links und rechts
	float side = smoothstep(0.018, 0.0, abs(UV.x - 0.035)) + smoothstep(0.018, 0.0, abs(UV.x - 0.965));
	// Warnstreifen vor dem Zaun
	float band = smoothstep(0.012, 0.0, abs(UV.y - fence_v + 0.012) - 0.012);
	float stripes = step(0.5, fract((UV.x * 9.0 + UV.y * 40.0)));
	col = mix(col, mix(line_col, warn_col, stripes), band);
	// Laufrichtung: dezente Pfeile zur Station hin
	float arrows = smoothstep(0.03, 0.0, abs(fract(UV.y * 9.0 - TIME * 0.25 + abs(UV.x - 0.5) * 1.4) - 0.5) - 0.02);
	float lane = smoothstep(0.08, 0.0, abs(UV.x - 0.5) - 0.06) * step(UV.y, fence_v - 0.03);
	ALBEDO = col;
	METALLIC = 0.55;
	ROUGHNESS = 0.5;
	EMISSION = glow_col * side * 2.0 + glow_col * arrows * lane * 0.12;
}
