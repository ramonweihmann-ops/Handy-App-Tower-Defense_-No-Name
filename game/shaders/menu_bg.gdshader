shader_type canvas_item;
// Menü-Hintergrund: warmer Verlauf von Indigo zu Magenta, weiche schwebende Lichtpunkte, Sterne.

uniform vec2 aspect = vec2(0.5625, 1.0);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 uv = UV;
	vec3 top = vec3(0.16, 0.08, 0.36);
	vec3 mid = vec3(0.36, 0.12, 0.46);
	vec3 bot = vec3(0.55, 0.16, 0.38);
	vec3 col = mix(top, mid, smoothstep(0.0, 0.55, uv.y));
	col = mix(col, bot, smoothstep(0.55, 1.0, uv.y));
	// weiches Licht von oben
	col += vec3(0.25, 0.15, 0.35) * smoothstep(0.7, 0.0, length((uv - vec2(0.5, 0.1)) * aspect / aspect.x));
	// schwebende Lichtpunkte (Bokeh)
	for (int i = 0; i < 14; i++) {
		float fi = float(i);
		vec2 c = vec2(hash(vec2(fi, 1.3)), fract(hash(vec2(fi, 7.1)) - TIME * (0.008 + 0.012 * hash(vec2(fi, 3.3)))));
		c.x += sin(TIME * 0.3 + fi) * 0.03;
		float r = 0.03 + 0.07 * hash(vec2(fi, 5.7));
		float d = length((uv - c) * aspect / aspect.x);
		vec3 tint = mix(vec3(1.0, 0.6, 0.4), vec3(0.6, 0.5, 1.0), hash(vec2(fi, 9.9)));
		col += tint * smoothstep(r, r * 0.2, d) * 0.12;
	}
	// feine Sterne
	vec2 g = uv * aspect / aspect.x * 70.0;
	float h = hash(floor(g));
	col += vec3(1.0) * step(0.985, h) * smoothstep(0.3, 0.0, length(fract(g) - 0.5)) * (0.5 + 0.5 * sin(TIME * 2.0 + h * 30.0)) * 0.6;
	COLOR = vec4(col, 1.0);
}
