#!/usr/bin/env python3
"""Genera un reel de Salió caro a partir de <carpeta>/script.json.

  python3 make_reel.py <carpeta>              -> <carpeta>/reel.mp4 (+ voice.wav, timings.json)
  python3 make_reel.py <carpeta> --stills     -> PNGs de control en <carpeta>/stills/ (sin vídeo)

Formato del script.json: ver GUIA.md en esta misma carpeta.
"""
import json, math, os, re, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

CACHE = os.path.expanduser("~/.cache/saliocaro")
W, H, FPS = 1080, 1920, 30
BG = (14, 14, 16); WHITE = (245, 242, 236); RED = (232, 52, 44); DIM = (120, 118, 114)
ANTON = os.path.join(CACHE, "fonts/Anton.woff")
IB = os.path.join(CACHE, "fonts/Inter-Bold.woff")
IM = os.path.join(CACHE, "fonts/Inter-Medium.woff")
X0, XMAX, CX = 80, 850, 465      # zona segura: 230 px libres a la derecha (botones de Instagram)
TOP, BOT = 240, 1440             # zona segura vertical (caption abajo)
CAP_Y = 1320                     # línea de subtítulos
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
# Pronunciación: 1) marcas y anglicismos frecuentes escritos "a la española" (como se dicen en España);
# 2) cualquier otra palabra que sea claramente inglesa se pronuncia con fonemas ingleses (detección por frecuencia de uso).
PRON = {"Toys R Us": "Tois ar as", "Toys \"R\" Us": "Tois ar as", "Pryca": "Prica", "Amazon": "Ámazon", "iPhone": "aifon",
        "Google": "Gúgel", "Facebook": "Feisbuk", "Microsoft": "Máicrosoft", "Blockbuster": "Blocbaster", "GoPro": "Goupro",
        "Lycos": "Láicos", "YouTube": "Yutub", "BlackBerry": "Blacberri", "Windows": "Güindous", "Xbox": "Equisbox",
        "Netflix": "Nétflix", "Apple": "Ápel", "Twitter": "Tuíter", "Instagram": "Ínstagram", "WhatsApp": "Guasap",
        "Starbucks": "Estárbucs", "McDonald's": "Macdónalds", "Burger King": "Burguer King", "Walmart": "Guólmart",
        "Kodak": "Códac", "Nokia": "Nóquia", "Motorola": "Motorola", "Tesla": "Tesla", "Uber": "Úber", "Airbnb": "Erbiembí",
        "Juicero": "Yusero", "WeWork": "Güiguork", "Quibi": "Quibi", "Sears": "Siers", "Pan Am": "Pan Am", "Disney": "Dísni"}
ANGL = {"online": "onláin", "offline": "ofláin", "marketing": "márketin", "startup": "estártap", "startups": "estártaps",
        "software": "sófgüer", "hardware": "járgüer", "email": "ímeil", "e-mail": "ímeil", "delivery": "delíveri",
        "streaming": "estrímin", "CEO": "si i ou", "marketplace": "márquetpleis", "smartphone": "esmártfon",
        "smartphones": "esmártfons", "podcast": "pódcast", "influencer": "inflúenser", "influencers": "inflúensers",
        "low cost": "lou cost", "retail": "ríteil", "stock": "estoc", "outlet": "áutlet", "e-commerce": "icómers",
        "ecommerce": "icómers", "boom": "bum", "show": "chou", "app": "ap", "apps": "aps", "chat": "chat",
        "blockbuster": "blocbaster", "brand": "brand", "branding": "brándin", "business": "bísnes", "feedback": "fídbac",
        "manager": "mánayer", "marketplaces": "márquetpleises", "premium": "prímium", "ranking": "ránquin",
        "web": "güeb", "big data": "big data", "fake": "feik", "hype": "jaip", "trending": "tréndin", "dot-com": "dot com",
        "puntocom": "puntocom", "leasing": "lísin", "holding": "jóldin", "lobby": "lobi", "sponsor": "espónsor"}
_RX = None
def pron(text):
    import re as _re
    global _RX
    for k2, v in PRON.items(): text = text.replace(k2, v)
    if _RX is None:
        keys = sorted(ANGL, key=len, reverse=True)
        _RX = _re.compile(r"(?<![\wáéíóúñ])(" + "|".join(_re.escape(k2) for k2 in keys) + r")(?![\wáéíóúñ])", _re.I)
    return _RX.sub(lambda m: ANGL.get(m.group(1), ANGL.get(m.group(1).lower(), m.group(1))), text)

def is_english(word):
    """Palabra claramente inglesa que no se usa en castellano (ni lleva acentos ni ñ)."""
    import re as _re
    w = _re.sub(r"[^\w'-]", "", word)
    if not w or _re.search(r"[áéíóúñü\d]", w.lower()) or len(w) < 3: return False
    try:
        from wordfreq import zipf_frequency as z
    except Exception:
        return False
    en, es = z(w.lower(), "en"), z(w.lower(), "es")
    return es < 3.3 and en - es >= 1.0

def to_phonemes(k, text):
    """Fonemas mezclando castellano e inglés según cada palabra."""
    import re as _re
    toks = _re.findall(r"[\w'’-]+|[^\w\s]", text)
    groups, cur, lang = [], [], None
    for tk in toks:
        lg = "en-us" if _re.match(r"[\w'’-]+$", tk) and is_english(tk) else ("es" if _re.match(r"[\w'’-]+$", tk) else lang or "es")
        if lang and lg != lang: groups.append((lang, " ".join(cur))); cur = []
        cur.append(tk); lang = lg
    if cur: groups.append((lang, " ".join(cur)))
    if all(g[0] == "es" for g in groups): return None
    return " ".join(k.tokenizer.phonemize(g, lg) for lg, g in groups)

def make_voice(folder, lines):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(CACHE, "kokoro-v1.0.onnx"), os.path.join(CACHE, "voices-v1.0.bin"))
    sr, GAP, t = 24000, 0.10, 0.15
    pieces = [np.zeros(int(0.15 * sr), np.float32)]
    for l in lines:
        # fluidez: los puntos internos se leen como comas (sin pausa larga); el subtítulo no cambia
        say = re.sub(r"(?<=[^\d])\.\s+(\S)", lambda m: ", " + m.group(1).lower(), pron(l["say"].strip()))
        ph = to_phonemes(k, say)
        if ph: a, sr = k.create(ph, voice="em_alex", speed=1.15, lang="es", is_phonemes=True)
        else: a, sr = k.create(say, voice="em_alex", speed=1.15, lang="es")
        a = a.astype(np.float32)
        idx = np.where(np.abs(a) > 0.008)[0]
        a = a[max(0, idx[0] - 240): idx[-1] + 480]
        l["start"], l["end"] = t, t + len(a) / sr
        pieces += [a, np.zeros(int(GAP * sr), np.float32)]; t += len(a) / sr + GAP
    pieces.append(np.zeros(int(0.6 * sr), np.float32))
    full = np.concatenate(pieces); full = full / np.abs(full).max() * 0.9
    sf.write(os.path.join(folder, "voice.wav"), full, sr)
    return len(full) / sr

# ------------------------------------------------------------------ música de fondo (generada, sin derechos)
def make_music(folder, total, lines, bpm=96, seed=0):
    """Base sintética de tensión: bombo, hi-hat, bajo en La menor y pad; 'whoosh' en cada cambio de tarjeta."""
    import soundfile as sf
    sr = 44100; n = int((total + 1) * sr); t = np.arange(n) / sr
    out = np.zeros(n, np.float32); beat = 60 / bpm
    rng = np.random.default_rng(seed)
    def env(length, decay):
        x = np.arange(int(length * sr)) / sr; return np.exp(-x * decay)
    kick = (np.sin(2 * np.pi * (50 + 90 * env(0.25, 30)) * np.arange(int(0.25 * sr)) / sr) * env(0.25, 12)).astype(np.float32)
    hat = (rng.standard_normal(int(0.05 * sr)) * env(0.05, 90)).astype(np.float32)
    hat = np.diff(hat, prepend=0).astype(np.float32)
    roots = [55.0, 55.0, 43.65, 49.0]   # La, La, Fa, Sol (graves)
    k = 0; x = 0.0
    while x < total + 1:
        i = int(x * sr)
        if k % 4 in (0, 2): out[i:i + len(kick)] += kick[: max(0, min(len(kick), n - i))] * 0.9
        for h in (0, 0.5):
            j = int((x + h * beat) * sr); out[j:j + len(hat)] += hat[: max(0, min(len(hat), n - j))] * 0.18
        f = roots[(k // 8) % 4]; L = int(beat * sr); seg = np.arange(min(L, n - i)) / sr
        out[i:i + len(seg)] += (np.sign(np.sin(2 * np.pi * f * seg)) * 0.10 * np.exp(-seg * 3)).astype(np.float32)
        x += beat; k += 1
    for f, a in ((220.0, .05), (261.6, .04), (329.6, .035)):   # pad Lam suave
        out += (a * np.sin(2 * np.pi * f * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))).astype(np.float32)
    starts, last = [], None
    for l in lines:
        if l.get("card") not in (None, "same") and l.get("card") != last: starts.append(l["start"])
        if l.get("card") not in (None, "same"): last = l.get("card")
    for st in starts[1:]:
        L = int(0.35 * sr); i = int(max(0, st - 0.15) * sr)
        w = rng.standard_normal(L).astype(np.float32); w = np.convolve(w, np.ones(30) / 30, mode="same")
        e = np.sin(np.linspace(0, np.pi, L)) ** 2
        out[i:i + L] += (w * e * 0.9)[: max(0, min(L, n - i))]
    out = out / np.abs(out).max() * 0.8
    fade = int(1.2 * sr); out[-fade:] *= np.linspace(1, 0, fade)
    sf.write(os.path.join(folder, "music.wav"), out, sr)

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
            by = cy + (400 if kind == "year" else 190)
            d2.rounded_rectangle((X0, by, X0 + w, by + 140), radius=24, fill=RED)
            d2.text((X0 + w / 2, by + 70), l["badge"], font=f, fill=WHITE, anchor="mm")
            self.comp(im, l2, ease(lt / 0.2), 0.6 + 0.4 * p2, center=(X0 + w / 2, by + 70))

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


# ------------------------------------------------------------------ imágenes (Wikimedia Commons, licencias libres)
def commons_search(q, n=10):
    import urllib.parse, time
    UA = "SalioCaroBot/1.0 (https://github.com/Fmochy/salio-caro-reels)"
    u = ("https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=" + urllib.parse.quote(q) +
         f"&gsrnamespace=6&gsrlimit={n}&prop=imageinfo&iiprop=size|extmetadata&iiextmetadatafilter=LicenseShortName|Artist&format=json")
    for t in range(6):
        r = subprocess.run(["curl", "-s", "-A", UA, u], capture_output=True, text=True).stdout
        try: d = json.loads(r); break
        except Exception: time.sleep(8 * (t + 1)); d = {}
    out = []
    for p in d.get("query", {}).get("pages", {}).values():
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        art = re.sub(r"<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()[:60]
        out.append({"file": p["title"], "w": ii["width"], "h": ii["height"], "license": m.get("LicenseShortName", {}).get("value", ""), "author": art})
    return out

def commons_download(file_title, dest, credits_path=None, meta=None):
    import urllib.parse, time
    name = file_title.replace("File:", "").replace(" ", "_")
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=1280"
    for t in range(5):
        subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0 SalioCaro", "-o", dest, url])
        if os.path.exists(dest) and open(dest, "rb").read(3) in (b"\xff\xd8\xff", b"\x89PN"): break
        time.sleep(10 * (t + 1))
    else:
        return False
    if credits_path:
        cr = json.load(open(credits_path)) if os.path.exists(credits_path) else []
        cr.append({"file": file_title, "dest": os.path.basename(dest), **(meta or {})})
        json.dump(cr, open(credits_path, "w"), ensure_ascii=False, indent=1)
    return True

# ------------------------------------------------------------------ formato v2 (fotos reales)
M = sys.modules[__name__]
FB = os.path.join(CACHE, "fonts/MontBlack.woff"); FX = os.path.join(CACHE, "fonts/MontXB.woff")
YEL = (255, 212, 0); WHITE2 = (255, 255, 255); BLACK = (12, 12, 12); RED2 = (230, 40, 40)
CX2 = 470                # centro útil (230 px de la derecha los tapan los botones)
CAP_Y2 = 1380             # subtítulos abajo y centrados, por encima del texto del caption de Instagram
CXC = 540                # centro real de la pantalla para los subtítulos


class V2:
    def __init__(self, data, total, folder):
        self.d, self.total, self.folder = data, total, folder
        self.lines = data["lines"]; self.cache = {}
        # línea de tiempo de visuales: reparte cada frase entre sus visuales según el reparto de palabras
        self.beats = []
        for li, l in enumerate(self.lines):
            vs = l.get("visuals") or [{"type": "img", "src": self.lines[li - 1]["visuals"][-1].get("src")}]
            n = len(vs); dur = (l["end"] - l["start"])
            for k, v in enumerate(vs):
                s = l["start"] + dur * k / n; e = l["start"] + dur * (k + 1) / n
                self.beats.append({**v, "s": s, "e": e, "line": li, "k": k})
        for i, b in enumerate(self.beats):        # cubrir huecos entre frases
            b["e2"] = self.beats[i + 1]["s"] if i + 1 < len(self.beats) else total
        self.words = M.Reel.__new__(M.Reel); self.words.lines = self.lines
        self._build_words()

    def _build_words(self):
        import re
        self.ws = []
        for li, l in enumerate(self.lines):
            ws = l["show"].split(); reds = set(l.get("red", []))
            wts = [len(re.sub(r"\W", "", w)) + 2 for w in ws]; tot, acc = sum(wts), l["start"]
            for w, wt in zip(ws, wts):
                dd = (l["end"] - l["start"]) * wt / tot
                self.ws.append({"w": w, "s": acc, "e": acc + dd, "line": li, "red": w in reds or w.strip(".,?!:¿¡") in reds}); acc += dd
        self.chunks, cur = [], []
        for w in self.ws:   # 1-3 palabras, corta en puntuación
            if cur and (cur[-1]["line"] != w["line"] or len(cur) >= 3 or re.search(r"[.,?!:]$", cur[-1]["w"])):
                self.chunks.append(cur); cur = []
            cur.append(w)
        self.chunks.append(cur)

    # ---------- recursos
    def img(self, src):
        if src not in self.cache:
            im = Image.open(os.path.join(self.folder, src)).convert("RGB")
            s = max(W / im.width, H / im.height) * 1.16
            im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
            im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.12)).enhance(1.06)
            self.cache[src] = im
        return self.cache[src]

    def bg(self, b, t, dark=0.0):
        im = self.img(b["src"]); p = max(0, min(1, (t - b["s"]) / max(0.2, b["e2"] - b["s"])))
        z = (1.0 + 0.06 * p) if b.get("zoom", "in") == "in" else (1.06 - 0.06 * p)
        punch = 1 + 0.07 * (1 - ease((t - b["s"]) / 0.22))
        z *= punch
        cw, ch = int(W * 1.12 / z), int(H * 1.12 / z)
        fx, fy = b.get("focus", [0.5, 0.45])
        cx = min(max(cw / 2, fx * im.width), im.width - cw / 2); cy = min(max(ch / 2, fy * im.height), im.height - ch / 2)
        fr = im.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BILINEAR)
        if dark: fr = ImageEnhance.Brightness(fr).enhance(1 - dark)
        return fr.convert("RGBA")

    def boxtext(self, d, x, y, text, font, fg, bgc, pad=(26, 14), anchor="mm"):
        w = d.textlength(text, font=font); h = font.size
        x0 = x - w / 2 - pad[0] if anchor == "mm" else x - pad[0]
        d.rounded_rectangle((x0, y - h * 0.62 - pad[1], x0 + w + 2 * pad[0], y + h * 0.62 + pad[1]), radius=16, fill=bgc)
        d.text((x0 + pad[0], y), text, font=font, fill=fg, anchor="lm")

    def fit(self, d, text, path, size, maxw):
        f = F(path, size)
        while d.textlength(text, font=f) > maxw and f.size > 28: f = F(path, f.size - 4)
        return f

    # ---------- visuales
    def draw_beat(self, b, t):
        typ = b.get("type", "img"); lt = t - b["s"]
        im = self.bg(b, t, dark=0.35 if typ in ("title", "number", "doc", "end") else 0.0)
        # degradado para legibilidad arriba y en la banda de subtítulos
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for y in range(0, 420, 6): d.rectangle((0, y, W, y + 6), fill=(0, 0, 0, int(120 * (1 - y / 420))))
        im.alpha_composite(lay)
        d = ImageDraw.Draw(im)
        if typ == "title":
            p = back(lt / 0.3)
            l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
            f1 = self.fit(d2, b["text1"].upper(), FB, 92, 820); f2 = self.fit(d2, b["text2"].upper(), FB, 108, 820)
            self.boxtext(d2, CX2, 560, b["text1"].upper(), f1, BLACK, WHITE2)
            self.boxtext(d2, CX2, 700, b["text2"].upper(), f2, BLACK, YEL)
            self.comp(im, l2, ease(lt / 0.12), 0.8 + 0.2 * p, (CX2, 630))
        elif typ == "number":
            pr = ease((lt - 0.05) / 0.9)
            txt = b.get("prefix", "") + M.fmt_num(b["value"] * pr) + b.get("suffix", "")
            f = self.fit(d, txt, FB, 170, 820)
            col = {"red": RED2, "yellow": YEL, "green": (40, 210, 90)}.get(b.get("color", "yellow"), YEL)
            d.text((CX2, 520), txt, font=f, fill=col, anchor="mm", stroke_width=8, stroke_fill=BLACK)
            if b.get("label"):
                self.boxtext(d, CX2, 680, b["label"].upper(), self.fit(d, b["label"].upper(), FX, 54, 760), BLACK, WHITE2)
        elif typ == "doc":
            p = back(lt / 0.35)
            paper = Image.new("RGBA", (760, 560), (250, 248, 242, 255)); pd = ImageDraw.Draw(paper)
            pd.text((40, 40), b.get("kicker", "DOCUMENTO").upper(), font=F(FX, 34), fill=(120, 30, 30))
            y = 110
            for line in b.get("lines", []):
                ff = self.fit(pd, line, FB, 64, 680); pd.text((40, y), line, font=ff, fill=BLACK); y += ff.size + 18
            for k in range(6): pd.line((40, y + 30 + k * 40, 720, y + 30 + k * 40), fill=(200, 196, 188), width=6)
            paper = paper.rotate(-4, expand=True, resample=Image.BICUBIC)
            s = 0.7 + 0.3 * p; paper = paper.resize((int(paper.width * s), int(paper.height * s)))
            im.alpha_composite(paper, (CX2 - paper.width // 2, 620 - paper.height // 2))
        elif typ == "end":
            f = F(FB, 190)
            d.text((CX2, 520), "SALIÓ", font=f, fill=WHITE2, anchor="mm", stroke_width=10, stroke_fill=BLACK)
            d.text((CX2, 720), "CARO.", font=f, fill=YEL, anchor="mm", stroke_width=10, stroke_fill=BLACK)
        if b.get("kicker") and typ in ("img",):
            p = back(lt / 0.25)
            k = b["kicker"].upper(); f = self.fit(d, k, FB, 96, 820)
            l2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
            d2.text((CX2, 470), k, font=f, fill=YEL if b.get("kcolor") != "white" else WHITE2, anchor="mm", stroke_width=8, stroke_fill=BLACK)
            self.comp(im, l2, ease(lt / 0.15), 0.7 + 0.3 * p, (CX2, 470))
        if b.get("stamp"):
            M.Reel.stamp(self, im, b["stamp"].upper(), 0.25, lt, CX2, 760, 150, -9)
        return im

    def layer(self): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def comp(self, im, lay, alpha=1.0, scale=1.0, center=(CX2, 700)):
        M.Reel.comp(self, im, lay, alpha, scale, center)

    def captions(self, im, t):
        style = os.environ.get("CAPSTYLE", "karaoke")
        ch = None
        for c in self.chunks:
            if c[0]["s"] - 0.03 <= t: ch = c
        if ch is None or t > ch[-1]["e"] + 0.35: return
        lay = self.layer(); d = ImageDraw.Draw(lay)
        if style == "palabra":            # una palabra cada vez, grande
            w = None
            for x in self.ws:
                if x["s"] - 0.03 <= t: w = x
            if w is None or t > w["e"] + 0.3: return
            txt = w["w"].upper().strip(",.:")
            f = self.fit(d, txt, FB, 120, 800)
            d.text((CX2, CAP_Y2), txt, font=f, fill=YEL if w["red"] else WHITE2, anchor="mm", stroke_width=10, stroke_fill=BLACK)
            self.comp(im, lay, ease((t - w["s"]) / 0.06))
            return
        if style == "caja":               # frase corta en caja blanca, clave en caja amarilla
            txts = [w["w"] for w in ch]
            f = self.fit(d, " ".join(txts), FX, 62, 780)
            sp = d.textlength(" ", font=f); tw = sum(d.textlength(x, font=f) for x in txts) + sp * (len(txts) - 1)
            x = CX2 - tw / 2; h = f.size
            d.rounded_rectangle((x - 22, CAP_Y2 - h * 0.75, x + tw + 22, CAP_Y2 + h * 0.75), radius=18, fill=WHITE2)
            for w, txt in zip(ch, txts):
                ww = d.textlength(txt, font=f)
                if w["red"]: d.rounded_rectangle((x - 8, CAP_Y2 - h * 0.62, x + ww + 8, CAP_Y2 + h * 0.62), radius=10, fill=YEL)
                d.text((x, CAP_Y2), txt, font=f, fill=BLACK, anchor="lm"); x += ww + sp
            self.comp(im, lay, ease((t - ch[0]["s"]) / 0.08))
            return
        # karaoke: 1-3 palabras fijas, la que suena se ilumina en amarillo
        txts = [w["w"].upper() for w in ch]
        f = self.fit(d, " ".join(txts), FB, 84, 740)
        x = CXC - d.textlength(" ".join(txts), font=f) / 2
        for w, txt in zip(ch, txts):
            on = w["s"] <= t < w["e"] + 0.05
            d.text((x, CAP_Y2), txt, font=f, fill=YEL if on else WHITE2, anchor="lm", stroke_width=9, stroke_fill=BLACK)
            x += d.textlength(txt + " ", font=f)
        im.alpha_composite(lay)

    def render(self, t):
        b = self.beats[0]
        for x in self.beats:
            if x["s"] <= t: b = x
        im = self.draw_beat(b, t)
        d = ImageDraw.Draw(im)   # marca discreta
        d.rounded_rectangle((60, 250, 262, 304), radius=27, fill=(230, 40, 40, 230))
        d.text((161, 277), "SALIÓ CARO", font=F(FX, 30), fill=WHITE2, anchor="mm")
        if self.lines[b["line"]].get("visuals") and b.get("type") == "follow" or (b["line"] == len(self.lines) - 1):
            lt = t - self.lines[-1]["start"]; p = back(lt / 0.4)
            if p > 0:
                l2 = self.layer(); d2 = ImageDraw.Draw(l2)
                d2.rounded_rectangle((CX2 - 230, 1140, CX2 + 230, 1240), radius=50, fill=RED2)
                d2.text((CX2, 1190), "SEGUIR", font=F(FB, 54), fill=WHITE2, anchor="mm")
                self.comp(im, l2, ease(lt / 0.2), 0.6 + 0.4 * p, (CX2, 1190))
        self.captions(im, t)
        if os.environ.get("LABEL"):
            d = ImageDraw.Draw(im); d.rounded_rectangle((CX2 - 300, 1500, CX2 + 300, 1600), radius=20, fill=(0, 0, 0, 200))
            d.text((CX2, 1550), os.environ["LABEL"], font=F(FB, 52), fill=YEL, anchor="mm")
        return im.convert("RGB")


def main_v2(folder, data):
    total = make_voice(folder, data["lines"])
    r = V2(data, total, folder); print(f"duración {total:.1f}s, {len(r.beats)} planos ({total / len(r.beats):.1f} s/plano)")
    if "--stills" in sys.argv:
        os.makedirs(os.path.join(folder, "stills"), exist_ok=True)
        for i, b in enumerate(r.beats):
            r.render(min(b["e"] - 0.05, b["s"] + 0.6)).save(os.path.join(folder, "stills", f"{i:02d}.png"))
        return
    # música con 'whoosh' en cada corte
    fake = [{"start": b["s"], "card": {"i": i}} for i, b in enumerate(r.beats)]
    M.make_music(folder, total, fake, seed=sum(map(ord, data.get("slug", "x"))))
    out = os.path.join(folder, "reel.mp4")
    fc = ("[1:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3,aresample=44100,asplit=2[v][key];"
          "[2:a]volume=0.26,lowpass=f=9000[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    p = subprocess.Popen([M.ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(folder, "voice.wav"), "-i", os.path.join(folder, "music.wav"),
                          "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(total * FPS)): p.stdin.write(r.render(fr / FPS).tobytes())
    p.stdin.close(); p.wait(); print("OK", out)


def main():
    if sys.argv[1] == "buscar":          # python3 make_reel.py buscar "texto"
        for r in commons_search(" ".join(sys.argv[2:])): print(json.dumps(r, ensure_ascii=False))
        return
    if sys.argv[1] == "bajar":           # python3 make_reel.py bajar "File:..." carpeta/img/x.jpg "autor" "licencia"
        ok = commons_download(sys.argv[2], sys.argv[3], os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[3]))), "credits.json"),
                              {"author": sys.argv[4] if len(sys.argv) > 4 else "", "license": sys.argv[5] if len(sys.argv) > 5 else ""})
        print("OK" if ok else "FALLO"); return
    folder = sys.argv[1]; stills = "--stills" in sys.argv
    data = json.load(open(os.path.join(folder, "script.json")))
    if any(l.get("visuals") for l in data["lines"]):
        return main_v2(folder, data)
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
    make_music(folder, total, data["lines"], seed=sum(map(ord, data.get("slug", "x"))))
    fc = ("[1:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3,aresample=44100,asplit=2[v][key];"
          "[2:a]volume=0.22,lowpass=f=9000[m];[m][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    p = subprocess.Popen([ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(folder, "voice.wav"), "-i", os.path.join(folder, "music.wav"),
                          "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(total * FPS)): p.stdin.write(reel.render(fr / FPS).tobytes())
    p.stdin.close(); p.wait()
    assert p.returncode == 0 and os.path.getsize(out) > 100_000, "falló ffmpeg"
    print("OK", out, os.path.getsize(out) // 1024, "KB")

if __name__ == "__main__":
    main()
