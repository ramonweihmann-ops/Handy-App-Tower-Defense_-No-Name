shader_type spatial;
// Das Wurmloch am Ende des Decks: wirbelnde Ringe mit hellem Kern.
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, shadows_disabled;

uniform vec3 c1 : source_color = vec3(0.62, 0.22, 1.0);
uniform vec3 c2 : source_color = vec3(0.1, 0.9, 0.85);
uniform float pulse = 0.0;

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float a = atan(p.y, p.x);
	float swirl = sin(a * 5.0 + r * 14.0 - TIME * 2.6) * 0.5 + 0.5;
	float swirl2 = sin(a * 3.0 - r * 9.0 + TIME * 1.7) * 0.5 + 0.5;
	float ring = smoothstep(1.0, 0.7, r) * smoothstep(0.08, 0.5, r);
	float core = smoothstep(0.5, 0.0, r);
	vec3 col = mix(c1, c2, swirl * swirl2) * ring * (0.45 + swirl);
	col += vec3(0.95, 0.85, 1.0) * core * (0.7 + pulse);
	ALBEDO = col;
	ALPHA = clamp(ring * (0.5 + swirl) + core, 0.0, 1.0) * smoothstep(1.0, 0.86, r);
}
