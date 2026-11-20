# Eiswelt: bereiftes Silberblau mit weißen Eisrissen, hellblaues Neon, Eiskristalle auf den Blöcken
CFG = {"block": (0.62, 0.72, 0.86), "deck": (0.36, 0.48, 0.66), "neon": (0.35, 0.8, 1.0), "metal": 0.55, "rough": 0.22,
       "block_cracks": (0.95, 0.98, 1.0), "deck_cracks": (0.9, 0.96, 1.0), "crystals": (0.35, 0.75, 1.0), "crystal_glow": 1.0, "crack_width": 0.02, "crack_mask": 0.4,
       "lamp": (0.4, 0.85, 1.0), "ambient": (0.08, 0.14, 0.3), "ambient_strength": 1.3, "sun": 2.8}
exec(open(os.path.join(KIT_DIR, "streng_kit.py")).read())
