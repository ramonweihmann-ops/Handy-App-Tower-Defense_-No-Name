shader_type canvas_item;
// Hintergrund des Ladebildschirms: Weltraum, Sterne und ein wirbelndes Wurmloch.

uniform vec2 aspect = vec2(0.5625, 1.0);
uniform vec2 hole_center = vec2(0.5, 0.36);

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 uv = UV;
	vec3 col = mix(vec3(0.02, 0.02, 0.07), vec3(0.09, 0.03, 0.16), smoothstep(1.0, 0.0, uv.y));
	// Nebel
	float neb = sin(uv.x * 5.0 + uv.y * 3.0 + TIME * 0.05) * sin(uv.y * 6.0 - uv.x * 2.0);
	col += vec3(0.3, 0.08, 0.4) * smoothstep(0.3, 1.0, neb) * 0.35;
	// Sterne
	vec2 grid = uv * aspect * 90.0;
	vec2 cell = floor(grid);
	float h = hash(cell);
	float star = step(0.97, h) * smoothstep(0.35, 0.0, length(fract(grid) - 0.5));
	col += vec3(0.9, 0.92, 1.0) * star * (0.5 + 0.5 * sin(TIME * (1.0 + h * 3.0) + h * 30.0));
	// Wurmloch
	vec2 p = (uv - hole_center) * aspect / aspect.x * 2.6;
	float r = length(p);
	float a = atan(p.y, p.x);
	float swirl = sin(a * 5.0 + r * 12.0 - TIME * 2.2) * 0.5 + 0.5;
	float ring = smoothstep(1.0, 0.7, r) * smoothstep(0.05, 0.5, r);
	vec3 hole = mix(vec3(0.62, 0.22, 1.0), vec3(0.1, 0.9, 0.85), swirl) * ring * (0.4 + swirl);
	hole += vec3(0.95, 0.85, 1.0) * smoothstep(0.45, 0.0, r) * 0.8;
	col += hole * 0.9;
	// Rand des Wurmlochs
	col += vec3(0.75, 0.4, 1.0) * smoothstep(0.04, 0.0, abs(r - 1.0)) * 0.8;
	COLOR = vec4(col, 1.0);
}
