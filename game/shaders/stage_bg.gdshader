shader_type canvas_item;
// Bild des gewählten Levels im Menü: Blick durch das Wurmloch in die Welt der Gegner.
// Abgerundete Ecken, weiche Vignette und ein leuchtender Boden für die Figuren.

uniform vec2 px_size = vec2(400.0, 600.0);
uniform float radius = 26.0;
uniform vec3 c1 : source_color = vec3(0.62, 0.22, 1.0);
uniform vec3 c2 : source_color = vec3(0.1, 0.9, 0.85);
uniform vec3 sky_top : source_color = vec3(0.1, 0.04, 0.22);
uniform vec3 sky_bottom : source_color = vec3(0.3, 0.1, 0.38);
uniform vec3 ground : source_color = vec3(0.45, 0.2, 0.55);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

float rounded_box(vec2 p, vec2 half_size, float r) {
	vec2 q = abs(p) - half_size + vec2(r);
	return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec2 uv = UV;
	vec2 px = uv * px_size;
	float aspect = px_size.x / px_size.y;
	vec3 col = mix(sky_top, sky_bottom, smoothstep(0.0, 0.75, uv.y));
	// Sterne
	vec2 g = vec2(uv.x * aspect, uv.y) * 40.0;
	float h = hash(floor(g));
	col += vec3(1.0) * step(0.965, h) * smoothstep(0.32, 0.0, length(fract(g) - 0.5)) * (0.55 + 0.45 * sin(TIME * 1.7 + h * 40.0));
	// Wurmloch
	vec2 p = (uv - vec2(0.5, 0.3)) * vec2(aspect, 1.0) * 3.4;
	float r = length(p);
	float a = atan(p.y, p.x);
	float swirl = sin(a * 5.0 + r * 11.0 - TIME * 1.6) * 0.5 + 0.5;
	float ring = smoothstep(1.0, 0.72, r) * smoothstep(0.04, 0.45, r);
	col = mix(col, mix(c1, c2, swirl) * (0.5 + swirl * 0.8), ring * 0.85);
	col += vec3(1.0, 0.95, 1.0) * smoothstep(0.42, 0.0, r) * 0.75;
	col += mix(c1, c2, 0.5) * smoothstep(1.4, 0.9, r) * smoothstep(0.85, 1.0, r) * 0.35;
	// Boden mit weichem Licht unter den Figuren
	float floor_y = smoothstep(0.6, 0.72, uv.y);
	vec2 f = (uv - vec2(0.5, 0.8)) * vec2(1.0, 3.2);
	col = mix(col, ground * (0.55 + 0.45 * (1.0 - uv.y)), floor_y * 0.85);
	col += mix(c1, c2, 0.35) * smoothstep(0.55, 0.0, length(f)) * 0.35;
	// Vignette
	col *= 1.0 - 0.45 * smoothstep(0.35, 0.95, length((uv - 0.5) * vec2(1.2, 1.0)));
	// abgerundete Ecken mit weicher Kante
	float d = rounded_box(px - px_size * 0.5, px_size * 0.5, radius);
	float alpha = clamp(0.5 - d, 0.0, 1.0);
	// heller Innenrand
	col += vec3(1.0, 0.9, 1.0) * smoothstep(3.0, 0.0, abs(d + 2.0)) * 0.18;
	COLOR = vec4(col, alpha);
}
