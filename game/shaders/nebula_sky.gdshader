shader_type sky;
// Weltraum wie im Mockup „Kampf“: dunkles Blau, lila und blaue Nebel, Sterne in zwei Größen.

float h3(vec3 p) { p = fract(p * 0.3183099 + 0.1); p *= 17.0; return fract(p.x * p.y * p.z * (p.x + p.y + p.z)); }
float n3(vec3 x) {
	vec3 i = floor(x); vec3 f = fract(x); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(h3(i), h3(i + vec3(1, 0, 0)), f.x), mix(h3(i + vec3(0, 1, 0)), h3(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(h3(i + vec3(0, 0, 1)), h3(i + vec3(1, 0, 1)), f.x), mix(h3(i + vec3(0, 1, 1)), h3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float fbm(vec3 p) { float a = 0.5; float s = 0.0; for (int i = 0; i < 5; i++) { s += a * n3(p); p *= 2.03; a *= 0.5; } return s; }

void sky() {
	vec3 d = EYEDIR;
	float n = fbm(d * 3.0 + vec3(1.7, 0.3, 4.1));
	float m = fbm(d * 6.0 + vec3(8.0, 2.0, 1.0));
	vec3 base = mix(vec3(0.01, 0.012, 0.05), vec3(0.04, 0.03, 0.12), clamp(d.y * 0.5 + 0.5, 0.0, 1.0));
	vec3 neb = vec3(0.45, 0.12, 0.6) * smoothstep(0.45, 0.85, n) + vec3(0.08, 0.3, 0.75) * smoothstep(0.5, 0.9, m) * 0.8;
	float st = step(0.9965, h3(floor(d * 420.0))) * (0.6 + 0.4 * h3(floor(d * 420.0) + 3.0));
	float st2 = step(0.999, h3(floor(d * 180.0))) * 1.5;
	COLOR = base + neb * 0.55 + vec3(st + st2);
}
