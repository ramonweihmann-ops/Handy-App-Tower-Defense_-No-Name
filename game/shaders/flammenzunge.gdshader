shader_type spatial;
// Weiche Flammenzunge für Fritzis Flammen (Fx3D.flame_burst): unbeleuchtet, Farbe und Deckkraft aus der Farbrampe der
// Teilchen (COLOR), Rand blendet weich aus (Blickwinkel zur Oberfläche), damit aus länglichen Kugeln züngelnde
// Flammen werden statt harter Bälle. Mitte heller als der Rand, wie bei echtem Feuer.
render_mode unshaded, blend_mix, depth_draw_never, cull_back, shadows_disabled;

void fragment() {
	float f = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	float edge = smoothstep(0.0, 0.45, f);
	ALBEDO = mix(COLOR.rgb, vec3(1.0, 0.97, 0.82), f * f * 0.55);
	ALPHA = COLOR.a * edge;
}
