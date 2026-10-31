#!/usr/bin/env python3
"""Erzeugt alle Klänge des Piloten synthetisch (keine fremden Dateien, keine Lizenzfragen).
Aufruf: python3 scripts/make_sounds.py  -> schreibt WAV-Dateien nach game/audio/"""
import math, os, random, struct, wave

RATE = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "game", "audio")
random.seed(7)


def write(name, samples):
    os.makedirs(OUT, exist_ok=True)
    peak = max(1e-6, max(abs(s) for s in samples))
    scale = 0.9 / peak
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s * scale)) * 32767)) for s in samples))


def env(t, a, d):
    """Kurzer Anstieg, dann exponentielles Abklingen."""
    return min(1.0, t / a) * math.exp(-t / d) if a > 0 else math.exp(-t / d)


def noise_lp(n, cutoff):
    """Rauschen mit einfachem Tiefpass (cutoff 0..1)."""
    out, y = [], 0.0
    for _ in range(n):
        y += cutoff * (random.uniform(-1, 1) - y)
        out.append(y)
    return out


def shot(dur=0.18, pitch=1.0, cutoff=0.5, body=180):
    n = int(RATE * dur)
    nz = noise_lp(n, cutoff)
    return [(nz[i] * 0.8 + 0.5 * math.sin(2 * math.pi * body * pitch * i / RATE * (1 - i / n * 0.5))) * env(i / RATE, 0.002, dur / 4) for i in range(n)]


def boom(dur=0.9):
    n = int(RATE * dur)
    nz = noise_lp(n, 0.08)
    return [(nz[i] * 1.2 + 0.6 * math.sin(2 * math.pi * (60 - 30 * i / n) * i / RATE)) * env(i / RATE, 0.005, 0.25) for i in range(n)]


def zap(dur=0.25, f0=1800, f1=300):
    n = int(RATE * dur)
    out, ph = [], 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        ph += 2 * math.pi * f / RATE
        s = math.copysign(1, math.sin(ph)) * 0.5 + random.uniform(-0.3, 0.3)
        out.append(s * env(i / RATE, 0.002, dur / 3))
    return out


def tone(freqs, dur, decay, wave_kind="sine", vib=0.0):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        s = 0.0
        for k, f in enumerate(freqs):
            ph = 2 * math.pi * f * t + vib * math.sin(2 * math.pi * 5 * t)
            if wave_kind == "sine":
                s += math.sin(ph) / (k + 1)
            else:
                s += (2 * ((ph / (2 * math.pi)) % 1) - 1) * 0.5 / (k + 1)
        out.append(s * env(t, 0.004, decay))
    return out


def seq(notes, step, decay=0.25, kind="sine"):
    out = []
    for f in notes:
        part = tone([f, f * 2], step, decay, kind)
        out += part
    return out + [0.0] * int(RATE * 0.3)


def note(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def music(bars=8, bpm=96):
    """Ruhige Schleife: weiche Flächen und ein leises Arpeggio in Moll."""
    beat = 60 / bpm
    chords = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]
    total = int(RATE * beat * 4 * bars)
    out = [0.0] * total
    for b in range(bars):
        ch = chords[b % len(chords)]
        start = int(RATE * beat * 4 * b)
        length = int(RATE * beat * 4)
        for i in range(length):
            t = i / RATE
            a = min(1.0, t / 0.4) * min(1.0, (length - i) / RATE / 0.4)
            s = sum(math.sin(2 * math.pi * note(n - 12) * t) for n in ch) / 3
            out[start + i] += s * a * 0.35
        for k in range(8):
            f = note(ch[k % 3] + (12 if k >= 4 else 0))
            st = start + int(RATE * beat * 0.5 * k)
            for i in range(int(RATE * beat * 0.5)):
                if st + i < total:
                    t = i / RATE
                    out[st + i] += math.sin(2 * math.pi * f * t) * math.exp(-t / 0.18) * 0.18
    return out


if __name__ == "__main__":
    write("shot", shot(0.16, 1.0, 0.45, 160))
    write("shot_light", shot(0.09, 1.6, 0.6, 260))
    write("shot_heavy", shot(0.32, 0.6, 0.3, 90))
    write("launch", [s * 0.8 for s in noise_lp(int(RATE * 0.35), 0.15)])
    write("boom", boom())
    write("zap", zap())
    write("frost", zap(0.3, 2600, 1200))
    write("flame", [s * env(i / RATE, 0.01, 0.12) for i, s in enumerate(noise_lp(int(RATE * 0.25), 0.25))])
    write("pop", tone([520, 780], 0.14, 0.05))
    write("clack", tone([1900, 3100], 0.05, 0.012))
    write("ding", tone([1320, 1980], 0.35, 0.12))
    write("spring", zap(0.3, 200, 900))
    write("click", tone([900], 0.06, 0.015))
    write("whoosh", [s * math.sin(math.pi * i / int(RATE * 0.5)) for i, s in enumerate(noise_lp(int(RATE * 0.5), 0.2))])
    write("levelup", seq([note(n) for n in (72, 76, 79, 84)], 0.09, 0.2))
    write("win", seq([note(n) for n in (67, 72, 76, 79, 84, 88)], 0.12, 0.3))
    write("lose", seq([note(n) for n in (64, 60, 57, 52)], 0.22, 0.35, "saw"))
    write("music", music())
    print("Klänge erzeugt in", os.path.abspath(OUT))
