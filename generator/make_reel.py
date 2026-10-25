#!/usr/bin/env python3
"""Genera un reel de Salió caro a partir de <carpeta>/script.json.

  python3 make_reel.py <carpeta>              -> <carpeta>/reel.mp4 (+ voice.wav, timings.json)
  python3 make_reel.py <carpeta> --stills     -> PNGs de control en <carpeta>/stills/ (sin vídeo)

Formato del script.json: ver GUIA.md en esta misma carpeta.
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CACHE = os.path.expanduser("~/.cache/saliocaro")
W, H, FPS = 1080, 1920, 30
BG = (14, 14, 16); WHITE = (245, 242, 236); RED = (232, 52, 44); DIM = (120, 118, 114)
ANTON = os.path.join(CACHE, "fonts/Anton.woff")
IB = os.path.join(CACHE, "fonts/Inter-Bold.woff")
IM = os.path.join(CACHE, "fonts/Inter-Medium.woff")
X0, XMAX, CX = 80, 850, 465      # zona segura: 230 px libres a la derecha (botones de Instagram)
TOP, BOT = 240, 1440             # zona segura vertical (caption abajo)
CAP_Y = 1230                     # línea de subtítulos
_fc = {}
def F(p, s):
    k = (p, int(s))
    if k not in _fc: _fc[k] = ImageFont.truetype(p, int(s))
    return _fc[k]

def ease(t): t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3
def back(t):
    t = max(0.0, min(1.0, t)); c = 1.7; return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
def fmt_num(v): return f"{int(round(v)):,}".replace(",", ".")

# ------------------------------------------------------------------ voz
def make_voice(folder, lines):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(CACHE, "kokoro-v1.0.onnx"), os.path.join(CACHE, "voices-v1.0.bin"))
    sr, GAP, t = 24000, 0.22, 0.15
    pieces = [np.zeros(int(0.15 * sr), np.float32)]
    for l in lines:
        a, sr = k.create(l["say"], voice="em_alex", speed=1.1, lang="es")
        a = a.astype(np.float32)
        idx = np.where(np.abs(a) > 0.008)[0]
        a = a[max(0, idx[0] - 240): idx[-1] + 960]
        l["start"], l["end"] = t, t + len(a) / sr
        pieces += [a, np.zeros(int(GAP * sr), np.float32)]; t += len(a) / sr + GAP
    pieces.append(np.zeros(int(0.6 * sr), np.float32))
    full = np.concatenate(pieces); full = full / np.abs(full).max() * 0.9
    sf.write(os.path.join(folder, "voice.wav"), full, sr)
    return len(full) / sr

# ------------------------------------------------------------------ escena
class Reel:
    def __init__(self, data, total):
        self.d, self.lines, self.total = data, data["lines"], total
        # agrupa tarjetas: "card": "same" continúa la anterior
        gid, last = -1, None
        for l in self.lines:
            if l.get("card") in (None, "same") and last is not None:
                l["_card"], l["_gid"] = last, gid
            else:
                gid += 1; last = l["card"]; l["_card"], l["_gid"] = last, gid
        self.gstart = {}
        for l in self.lines: self.gstart.setdefault(l["_gid"], l["start"])
        self.words = []
        for li, l in enumerate(self.lines):
            ws = l["show"].split(); reds = set(l.get("red", []))
            wts = [len(re.sub(r"\W", "", w)) + 2 + (2 if re.search(r"[.,?!:]$", w) else 0) for w in ws]
            tot, acc = sum(wts), l["start"]
            for w, wt in zip(ws, wts):
                dd = (l["end"] - l["start"]) * wt / tot
                self.words.append({"w": w, "s": acc, "e": acc + dd, "line": li, "red": w in reds or w.strip(".,?!:¿¡") in reds})
                acc += dd
        self.chunks = self._chunks()
        base = Image.new("RGB", (W, H), BG)
        glow = Image.new("RGB", (W + 800, H + 800), BG); gd = ImageDraw.Draw(glow)
        gd.ellipse((200, 700, 1300, 1700), fill=(70, 14, 12))
        self.base, self.glow = base, glow.filter(ImageFilter.GaussianBlur(220))

    def _chunks(self):
        out, cur = [], []
        probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        for w in self.words:
            test = cur + [w]
            txt = " ".join(x["w"] for x in test).upper()
            if cur and (cur[-1]["line"] != w["line"] or len(test) > 3 or probe.textlength(txt, font=F(ANTON, 104)) > XMAX - X0
                        or re.search(r"[.,?!:]$", cur[-1]["w"])):
                out.append(cur); cur = [w]
            else: cur = test
        out.append(cur); return out

    def line_at(self, t):
        for i, l in enumerate(self.lines):
            nxt = self.lines[i + 1]["start"] if i + 1 < len(self.lines) else 1e9
            if t < nxt: return i
        return len(self.lines) - 1

    # ---- utilidades de dibujo
    @staticmethod
    def layer(): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def comp(self, im, lay, alpha=1.0, scale=1.0, center=(CX, 700)):
        if alpha <= 0: return
        if scale != 1.0:
            lay = lay.resize((int(W * scale), int(H * scale)), Image.BICUBIC)
            big = self.layer(); big.paste(lay, (int(center[0] - center[0] * scale), int(center[1] - center[1] * scale))); lay = big
        if alpha < 1: lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
        im.alpha_composite(lay)
    def stamp(self, im, text, t_in, lt, cx, cy, size=120, rot=-9):
        p = ease((lt - t_in) / 0.16)
        if p <= 0: return
        f = F(ANTON, size)
        while ImageDraw.Draw(self.layer()).textlength(text, font=f) > XMAX - X0 - 120: f = F(ANTON, f.size - 6)
        w = int(ImageDraw.Draw(self.layer()).textlength(text, font=f)) + 80
        s_img = Image.new("RGBA", (w, int(f.size * 1.6)), (0, 0, 0, 0)); sd = ImageDraw.Draw(s_img)
        sd.rectangle((6, 6, w - 6, s_img.height - 6), outline=RED, width=12)
        sd.text((w // 2, s_img.height // 2 + 4), text, font=f, fill=RED, anchor="mm")
        s = 1 + 0.7 * (1 - p)
        s_img = s_img.resize((int(s_img.width * s), int(s_img.height * s))).rotate(rot, expand=True, resample=Image.BICUBIC)
        s_img.putalpha(s_img.getchannel("A").point(lambda v: int(v * p)))
        im.alpha_composite(s_img, (cx - s_img.width // 2, cy - s_img.height // 2))
    def fit(self, d, txt, font_path, size, maxw):
        f = F(font_path, size)
        while d.textlength(txt, font=f) > maxw and f.size > 30: f = F(font_path, f.size - 4)
        return f

    # ---- tarjetas
    def card(self, im, li, t):
        l = self.lines[li]; c = l["_card"]; kind = c["type"]
        ct = t - self.gstart[l["_gid"]]; lt = t - l["start"]
        a_in = ease(ct / 0.25); sc = 0.92 + 0.08 * back(ct / 0.35)
        lay = self.layer(); d = ImageDraw.Draw(lay); cy = 700
        if kind == "money":
            p = ease((ct - 0.1) / 1.8)
            txt = c.get("prefix", "") + fmt_num(c["value"] * p) + c.get("suffix", "")
            f = self.fit(d, txt, ANTON, 170, XMAX - X0)
            if c.get("label"): d.text((X0, cy - 160), c["label"].upper(), font=self.fit(d, c["label"].upper(), IB, 34, XMAX - X0), fill=DIM)
            d.text((X0, cy - 100), txt, font=f, fill=RED if c.get("color", "red") == "red" else WHITE)
            if c.get("unit"): d.text((X0, cy + 110), c["unit"].upper(), font=F(IB, 34), fill=DIM)
            self.comp(im, lay, a_in, sc)
        elif kind == "year":
            d.text((CX, cy - 20), str(c["year"]), font=F(ANTON, 330), fill=(0, 0, 0, 0), stroke_width=4, stroke_fill=WHITE, anchor="mm")
            self.comp(im, lay, a_in, sc)
            for k, pill in enumerate(c.get("pills", [])[:2]):
                st = 0.6 + k * 1.4; p = back((ct - st) / 0.35)
                if p <= 0: continue
                col = RED if pill.get("color") == "red" else WHITE
                l2 = self.layer(); d2 = ImageDraw.Draw(l2)
                f2 = self.fit(d2, pill["text"].upper(), ANTON, 64, XMAX - X0 - 80); w = d2.textlength(pill["text"].upper(), font=f2) + 70
                y = cy + 170 + k * 120
                d2.rounded_rectangle((CX - w / 2, y - 50, CX + w / 2, y + 50), radius=50, fill=col)
                d2.text((CX, y), pill["text"].upper(), font=f2, fill=BG if col == WHITE else WHITE, anchor="mm")
                self.comp(im, l2, ease((ct - st) / 0.2), 0.5 + 0.5 * p, center=(CX, y))
        elif kind == "place":
            p = back(ct / 0.5); px, py = CX, cy - 120 - int(40 * (1 - p))
            d.ellipse((px - 70, py - 70, px + 70, py + 70), fill=RED)
            d.polygon([(px - 58, py + 38), (px + 58, py + 38), (px, py + 150)], fill=RED)
            d.ellipse((px - 26, py - 26, px + 26, py + 26), fill=BG)
            d.ellipse((CX - 90, cy + 40, CX + 90, cy + 64), fill=(40, 40, 44))
            d.text((CX, cy + 160), c["title"].upper(), font=self.fit(d, c["title"].upper(), ANTON, 110, XMAX - X0), fill=WHITE, anchor="mm")
            if c.get("subtitle"): d.text((CX, cy + 250), c["subtitle"].upper(), font=self.fit(d, c["subtitle"].upper(), IB, 34, XMAX - X0), fill=DIM, anchor="mm")
            self.comp(im, lay, a_in, sc)
        elif kind == "versus":
            bw = XMAX - X0; r = max(0.06, min(1.0, float(c.get("b_ratio", 0.12))))
            p1 = ease((ct - 0.2) / 0.8); p2 = ease((ct - 1.2) / 0.6)
            d.text((X0, cy - 230), c["a_name"].upper(), font=self.fit(d, c["a_name"].upper(), ANTON, 64, bw), fill=WHITE)
            d.rectangle((X0, cy - 140, X0 + int(bw * p1), cy - 20), fill=WHITE)
            if p1 > 0.6: d.text((X0 + 30, cy - 80), c["a_label"].upper(), font=self.fit(d, c["a_label"].upper(), ANTON, 56, bw - 60), fill=BG, anchor="lm")
            d.text((X0, cy + 40), c["b_name"].upper(), font=self.fit(d, c["b_name"].upper(), ANTON, 64, bw), fill=RED)
            d.rectangle((X0, cy + 130, X0 + int(bw * r * p2), cy + 250), fill=RED)
            if p2 > 0.6:
                bx = X0 + int(bw * r) + 30 if r < 0.55 else X0 + 30
                d.text((bx, cy + 190), c["b_label"].upper(), font=self.fit(d, c["b_label"].upper(), ANTON, 56, XMAX - bx), fill=WHITE, anchor="lm")
            self.comp(im, lay, a_in)
        elif kind == "text":
            ls = [x.upper() for x in c["lines"]][:3]
            n = len(ls); size = 230 if n <= 2 else 170
            shake = int(8 * math.sin(ct * 60) * max(0, 1 - ct / 0.4))
            for k, s in enumerate(ls):
                f = self.fit(d, s, ANTON, size, XMAX - X0)
                y = cy + (k - (n - 1) / 2) * size * 1.0
                d.text((CX + (shake if k % 2 == 0 else -shake), y), s, font=f, fill=RED if k == n - 1 else WHITE, anchor="mm")
            self.comp(im, lay, a_in, 0.85 + 0.15 * back(ct / 0.4))
        elif kind == "follow":
            d.ellipse((CX - 120, cy - 260, CX + 120, cy - 20), fill=RED)
            d.text((CX, cy - 165), "SALIÓ", font=F(ANTON, 70), fill=WHITE, anchor="mm")
            d.text((CX, cy - 95), "CARO", font=F(ANTON, 70), fill=WHITE, anchor="mm")
            d.text((CX, cy + 60), "@salio.caro", font=F(IB, 56), fill=WHITE, anchor="mm")
            self.comp(im, lay, a_in, sc)
            p = back((ct - 0.5) / 0.4)
            if p > 0:
                l2 = self.layer(); d2 = ImageDraw.Draw(l2)
                d2.rounded_rectangle((CX - 220, cy + 140, CX + 220, cy + 250), radius=55, fill=RED)
                d2.text((CX, cy + 195), "SEGUIR", font=F(ANTON, 64), fill=WHITE, anchor="mm")
                self.comp(im, l2, ease((ct - 0.5) / 0.2), 0.6 + 0.4 * p, center=(CX, cy + 195))
        # superposiciones por frase
        if l.get("stamp"):
            pos = {"money": (CX, cy + 300), "versus": (CX + 150, cy + 390), "year": (CX, cy - 10)}.get(kind, (CX, cy + 300))
            self.stamp(im, l["stamp"].upper(), 0.05 if kind != "year" else 0.4, lt, pos[0], pos[1], 140 if kind == "year" else 110, -7)
        if l.get("badge"):
            p2 = back(lt / 0.35); l2 = self.layer(); d2 = ImageDraw.Draw(l2)
            f = self.fit(d2, l["badge"], ANTON, 100, 560); w = d2.textlength(l["badge"], font=f) + 80
            d2.rounded_rectangle((X0, cy + 190, X0 + w, cy + 330), radius=24, fill=RED)
            d2.text((X0 + w / 2, cy + 260), l["badge"], font=f, fill=WHITE, anchor="mm")
            self.comp(im, l2, ease(lt / 0.2), 0.6 + 0.4 * p2, center=(X0 + w / 2, cy + 260))

    def captions(self, im, t):
        ch = None
        for c in self.chunks:
            if c[0]["s"] - 0.05 <= t: ch = c
        if ch is None or t > ch[-1]["e"] + 0.6: return
        ct = t - ch[0]["s"]; p = back(ct / 0.18)
        lay = self.layer(); d = ImageDraw.Draw(lay)
        txts = [w["w"].upper() for w in ch]
        f = self.fit(d, " ".join(txts), ANTON, 104, XMAX - X0)
        x = CX - d.textlength(" ".join(txts), font=f) / 2
        for w, txt in zip(ch, txts):
            col = (RED if w["red"] else WHITE) if w["s"] <= t else (95, 93, 90)
            d.text((x, CAP_Y), txt, font=f, fill=col, anchor="lm", stroke_width=3, stroke_fill=BG)
            x += d.textlength(txt + " ", font=f)
        self.comp(im, lay, ease(ct / 0.12), 0.85 + 0.15 * p, center=(CX, CAP_Y))

    def chrome(self, im, t):
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((X0, TOP + 20, X0 + 220, TOP + 80), radius=30, fill=RED)
        d.text((X0 + 110, TOP + 50), "SALIÓ CARO", font=F(ANTON, 36), fill=WHITE, anchor="mm")
        tag = self.d.get("tag", "").upper()
        if tag: d.text((XMAX, TOP + 50), tag, font=self.fit(d, tag, IB, 28, XMAX - X0 - 260), fill=DIM, anchor="rm")
        y = BOT - 10
        d.rectangle((X0, y, XMAX, y + 6), fill=(50, 50, 54))
        d.rectangle((X0, y, X0 + int((XMAX - X0) * min(1, t / self.total)), y + 6), fill=RED)

    def render(self, t):
        im = self.base.copy()
        im.paste(self.glow, (int(120 * math.sin(t * 0.35)) - 400, int(80 * math.cos(t * 0.27)) - 400))
        im = im.convert("RGBA")
        self.chrome(im, t); self.card(im, self.line_at(t), t); self.captions(im, t)
        return im.convert("RGB")

def ffmpeg_bin():
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: return "ffmpeg"

def main():
    folder = sys.argv[1]; stills = "--stills" in sys.argv
    data = json.load(open(os.path.join(folder, "script.json")))
    for l in data["lines"]:
        assert l.get("say") and l.get("show"), f"línea sin say/show: {l}"
    if data["lines"][0].get("card") in (None, "same"):
        sys.exit("la primera línea necesita una tarjeta")
    total = make_voice(folder, data["lines"])
    json.dump({"total": total, "lines": data["lines"]}, open(os.path.join(folder, "timings.json"), "w"), ensure_ascii=False, indent=1, default=str)
    reel = Reel(data, total)
    print(f"duración: {total:.1f} s")
    if total > 50: print("AVISO: dura más de 50 s, acorta el guion")
    if stills:
        os.makedirs(os.path.join(folder, "stills"), exist_ok=True)
        for i, l in enumerate(data["lines"]):
            tt = min(l["end"] - 0.1, l["start"] + 2.2)
            reel.render(tt).save(os.path.join(folder, "stills", f"{i:02d}.png"))
        print("stills en", os.path.join(folder, "stills")); return
    out = os.path.join(folder, "reel.mp4")
    p = subprocess.Popen([ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(folder, "voice.wav"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                          "-af", "highpass=f=80,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-14:TP=-1.5,aresample=44100",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(total * FPS)): p.stdin.write(reel.render(fr / FPS).tobytes())
    p.stdin.close(); p.wait()
    assert p.returncode == 0 and os.path.getsize(out) > 100_000, "falló ffmpeg"
    print("OK", out, os.path.getsize(out) // 1024, "KB")

if __name__ == "__main__":
    main()
