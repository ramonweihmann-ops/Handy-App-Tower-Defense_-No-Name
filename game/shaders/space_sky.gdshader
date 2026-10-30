shader_type sky;
// Weltraum-Hintergrund: Farbverlauf, Nebel und funkelnde Sterne.

float hash(vec3 p) {
	return fract(sin(dot(p, vec3(12.9898, 78.233, 45.164))) * 43758.5453);
}

void sky() {
	vec3 d = normalize(EYEDIR);
	vec3 col = mix(vec3(0.015, 0.015, 0.05), vec3(0.07, 0.03, 0.13), smoothstep(-0.3, 0.7, d.y));
	// Nebel
	float neb = sin(d.x * 3.1 + d.y * 2.3 + 1.2) * sin(d.z * 2.7 - d.y * 1.9) + 0.4 * sin(d.x * 7.0 - d.z * 5.0);
	col += vec3(0.32, 0.08, 0.42) * smoothstep(0.2, 1.1, neb) * 0.45;
	col += vec3(0.05, 0.25, 0.35) * smoothstep(0.4, 1.2, -neb) * 0.3;
	// Sterne in zwei Größen
	for (int i = 0; i < 2; i++) {
		float scale = i == 0 ? 160.0 : 70.0;
		vec3 p = d * scale;
		vec3 cell = floor(p);
		float h = hash(cell);
		vec3 f = fract(p) - 0.5;
		float threshold = i == 0 ? 0.975 : 0.992;
		float star = step(threshold, h) * smoothstep(0.32, 0.0, length(f));
		float twinkle = 0.6 + 0.4 * sin(TIME * (1.5 + h * 3.0) + h * 40.0);
		col += vec3(0.85, 0.9, 1.0) * star * twinkle * (i == 0 ? 0.9 : 1.4);
	}
	COLOR = col;
}
