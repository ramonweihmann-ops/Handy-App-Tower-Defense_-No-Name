shader_type canvas_item;
// Hintergrund hinter Fenstern wie im Mockup: weichgezeichnet (blur 4px) und abgedunkelt (rgba 10,6,30 · 70 %).
// Liest den schon gezeichneten Bildschirm darunter; 3 × 3 Abtastpunkte, damit es auf dem Handy günstig bleibt.

uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform float radius = 6.0;          // Bildpunkte
uniform vec4 shade : source_color = vec4(0.039, 0.024, 0.118, 0.7);

void fragment() {
	vec2 d = SCREEN_PIXEL_SIZE * radius;
	vec3 c = texture(screen_tex, SCREEN_UV).rgb * 4.0;
	c += (texture(screen_tex, SCREEN_UV + vec2(d.x, 0.0)).rgb + texture(screen_tex, SCREEN_UV - vec2(d.x, 0.0)).rgb
		+ texture(screen_tex, SCREEN_UV + vec2(0.0, d.y)).rgb + texture(screen_tex, SCREEN_UV - vec2(0.0, d.y)).rgb) * 2.0;
	c += texture(screen_tex, SCREEN_UV + d).rgb + texture(screen_tex, SCREEN_UV - d).rgb
		+ texture(screen_tex, SCREEN_UV + vec2(d.x, -d.y)).rgb + texture(screen_tex, SCREEN_UV + vec2(-d.x, d.y)).rgb;
	c /= 16.0;
	COLOR = vec4(mix(c, shade.rgb, shade.a), 1.0);
}
