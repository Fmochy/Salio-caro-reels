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

def make_voice_edge(folder, lines, voice="es-ES-AlvaroNeural", rate="+10%"):
    """Voz neuronal (edge-tts). Mismas marcas de tiempo que make_voice: rellena l["start"]/l["end"] y escribe voice.wav."""
    import asyncio, soundfile as sf
    try:
        import edge_tts
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "edge-tts"], check=False); import edge_tts
    if os.path.exists("/root/.ccr/ca-bundle.crt"): os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    sr, GAP, t = 24000, 0.08, 0.15
    pieces = [np.zeros(int(0.15 * sr), np.float32)]
    for i, l in enumerate(lines):
        say = re.sub(r"(?<=[^\d])\.\s+(\S)", lambda m: ", " + m.group(1).lower(), l["say"].strip())
        mp3 = os.path.join(folder, f"_v{i}.mp3"); wav = os.path.join(folder, f"_v{i}.wav")
        for intento in range(4):
            try:
                asyncio.run(edge_tts.Communicate(say, voice, rate=rate, proxy=proxy).save(mp3)); break
            except Exception as e:
                if intento == 3: raise
        subprocess.run([ffmpeg_bin(), "-y", "-loglevel", "error", "-i", mp3, "-ac", "1", "-ar", str(sr), wav], check=True)
        a, _ = sf.read(wav, dtype="float32"); os.remove(mp3); os.remove(wav)
        idx = np.where(np.abs(a) > 0.01)[0]
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
        if typ == "follow":
            im = self.bg(b, b["s"]).filter(ImageFilter.GaussianBlur(int(4 + 18 * ease(lt / 0.35))))
            return ImageEnhance.Brightness(im).enhance(1 - 0.55 * ease(lt / 0.35)).convert("RGBA")
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


    # ---------- cierre: tarjeta de perfil + "Seguir" que se pulsa solo
    def draw_follow(self, im, b, t):
        lt = t - b["s"]; IGB = (0, 149, 246)
        X0, X1, Y0, Y1 = CX2 - 380, CX2 + 380, 680, 1170
        # titular
        p = back(lt / 0.35)
        if p > 0:
            l2 = self.layer(); d2 = ImageDraw.Draw(l2)
            d2.text((CX2, 540), "¿TE HA GUSTADO?", font=self.fit(d2, "¿TE HA GUSTADO?", FB, 84, 820), fill=WHITE2, anchor="mm", stroke_width=8, stroke_fill=BLACK)
            self.comp(im, l2, ease(lt / 0.15), 0.7 + 0.3 * p, (CX2, 540))
        # tarjeta de perfil
        pc = back((lt - 0.15) / 0.4)
        if pc > 0:
            card = self.layer(); d = ImageDraw.Draw(card)
            d.rounded_rectangle((X0 + 8, Y0 + 14, X1 + 8, Y1 + 14), radius=44, fill=(0, 0, 0, 90))
            d.rounded_rectangle((X0, Y0, X1, Y1), radius=44, fill=(255, 255, 255, 255))
            ax, ay, ar = X0 + 130, Y0 + 140, 86
            for k in range(14):        # aro de historia (degradado naranja-rosa)
                a0 = k * 360 / 14
                c = tuple(int(u + (v - u) * k / 13) for u, v in zip((254, 196, 21), (216, 26, 136)))
                d.arc((ax - ar - 14, ay - ar - 14, ax + ar + 14, ay + ar + 14), a0 - 90, a0 - 90 + 360 / 14 + 2, fill=c, width=9)
            d.ellipse((ax - ar, ay - ar, ax + ar, ay + ar), fill=RED2)
            d.text((ax, ay - 20), "SALIÓ", font=F(FB, 38), fill=WHITE2, anchor="mm")
            d.text((ax, ay + 22), "CARO", font=F(FB, 38), fill=YEL, anchor="mm")
            d.text((X0 + 260, Y0 + 100), self.d.get("handle", "salio.caro"), font=F(FB, 50), fill=BLACK, anchor="lm")
            d.text((X0 + 260, Y0 + 160), "Errores de marcas", font=F(FX, 36), fill=(110, 110, 110), anchor="lm")
            d.text((X0 + 260, Y0 + 205), "que costaron millones", font=F(FX, 36), fill=(110, 110, 110), anchor="lm")
            d.text((CX2, Y0 + 300), "Un caso nuevo cada día", font=F(FX, 40), fill=BLACK, anchor="mm")
            # botón: azul "Seguir" -> gris "Siguiendo" con check
            tap = 1.55; bx0, by0, bx1, by1 = X0 + 50, Y0 + 360, X1 - 50, Y0 + 452
            if lt < tap:
                d.rounded_rectangle((bx0, by0, bx1, by1), radius=22, fill=IGB)
                d.text((CX2, (by0 + by1) // 2), "Seguir", font=F(FB, 46), fill=WHITE2, anchor="mm")
            else:
                d.rounded_rectangle((bx0, by0, bx1, by1), radius=22, fill=(239, 239, 239))
                f = F(FB, 46); tw = d.textlength("Siguiendo", font=f); cx = CX2 + 30; cy = (by0 + by1) // 2
                d.text((cx, cy), "Siguiendo", font=f, fill=BLACK, anchor="mm")
                q = ease((lt - tap) / 0.25); x = cx - tw / 2 - 64
                pts = [(x, cy), (x + 16, cy + 17), (x + 46, cy - 18)]
                if q > 0: d.line(pts[:2] if q < 0.4 else pts, fill=(30, 170, 80), width=9, joint="curve")
            s = 1.0 - 0.06 * max(0, 1 - abs(lt - tap) / 0.12)      # el botón "se hunde" al pulsar
            self.comp(im, card, ease((lt - 0.15) / 0.15), (0.75 + 0.25 * pc) * s, (CX2, (Y0 + Y1) // 2))
            # dedo que entra y pulsa
            if 0.9 < lt < tap + 0.7:
                u = ease((lt - 0.9) / (tap - 0.9 - 0.05))
                fx = int(X1 + 60 + (bx1 - 70 - X1 - 60) * u); fy = int(1500 + (by0 + 46 - 1500) * u)
                l3 = self.layer(); d3 = ImageDraw.Draw(l3)
                if lt >= tap:
                    rr = 40 + 120 * ease((lt - tap) / 0.45); al = int(220 * (1 - (lt - tap) / 0.7))
                    d3.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=(255, 255, 255, max(0, al)), width=8)
                al = int(255 * min(1, (tap + 0.7 - lt) / 0.25))
                d3.ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, int(al * 0.85)), outline=(20, 20, 20, al), width=5)
                im.alpha_composite(l3)
            # chispas al seguir
            if tap < lt < tap + 0.6:
                q = (lt - tap) / 0.6; l4 = self.layer(); d4 = ImageDraw.Draw(l4)
                for k in range(10):
                    a = k * 6.283 / 10; r0, r1 = 90 + 160 * q, 120 + 200 * q
                    cx, cy = CX2, (by0 + by1) // 2
                    d4.line((cx + r0 * math.cos(a) * 2.2, cy + r0 * math.sin(a), cx + r1 * math.cos(a) * 2.2, cy + r1 * math.sin(a)),
                            fill=(YEL if k % 2 else RED2) + (int(255 * (1 - q)),), width=9)
                im.alpha_composite(l4)
        # pie
        pf = back((lt - 2.0) / 0.35)
        if pf > 0:
            l5 = self.layer(); d5 = ImageDraw.Draw(l5)
            d5.text((CX2, 1300), "MAÑANA, OTRO CASO", font=self.fit(d5, "MAÑANA, OTRO CASO", FB, 70, 820), fill=YEL, anchor="mm", stroke_width=8, stroke_fill=BLACK)
            self.comp(im, l5, ease((lt - 2.0) / 0.15), 0.7 + 0.3 * pf, (CX2, 1300))
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
        if b.get("type") == "follow": return self.draw_follow(im, b, t).convert("RGB")
        d = ImageDraw.Draw(im)   # marca discreta
        d.rounded_rectangle((60, 250, 262, 304), radius=27, fill=(230, 40, 40, 230))
        d.text((161, 277), "SALIÓ CARO", font=F(FX, 30), fill=WHITE2, anchor="mm")
        if b.get("type") != "follow": self.captions(im, t)
        if os.environ.get("LABEL"):
            d = ImageDraw.Draw(im); d.rounded_rectangle((CX2 - 300, 1500, CX2 + 300, 1600), radius=20, fill=(0, 0, 0, 200))
            d.text((CX2, 1550), os.environ["LABEL"], font=F(FB, 52), fill=YEL, anchor="mm")
        return im.convert("RGB")


FOLLOW_SAY_BOLSA = ["Sígueme para entender la bolsa cada día.", "Sígueme, que mañana hay más bolsa.", "Si te ha servido, sígueme."]
FOLLOW_SAY = ["Sígueme, que mañana hay otro.",
              "Sígueme para más casos así.",
              "Si te ha gustado, sígueme."]

def prepare_follow(data):
    """El cierre siempre es la tarjeta de perfil: reutiliza la frase 'Sígueme' del guion o la añade."""
    L = data["lines"]
    src = None
    for l in L:
        for v in l.get("visuals") or []: src = v.get("src") or src
    say = FOLLOW_SAY[sum(map(ord, data.get("slug", "x"))) % len(FOLLOW_SAY)]
    if "ígueme" in L[-1].get("say", "") and len(L) > 1: L.pop()
    L.append({"say": say, "show": say, "visuals": [{"type": "follow", "src": src}]})

def main_v2(folder, data):
    import soundfile as sf
    prepare_follow(data)
    total = make_voice(folder, data["lines"])
    a, sr = sf.read(os.path.join(folder, "voice.wav"))       # 1,2 s más para que se vea el "Siguiendo"
    sf.write(os.path.join(folder, "voice.wav"), np.concatenate([a, np.zeros(int(1.2 * sr))]), sr); total += 1.2
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


# ================================================================== FORMATO 3 · HÍBRIDO (por defecto)
# Fotos reales impresas como polaroids sobre papel cuadriculado + anotaciones dibujadas a mano que se trazan mientras habla la voz.
# script.json: {"formato": "hibrido", "slug", "caption", "alt", "lines": [{"say", "show", "layout", "photos": [...], "notes": [...]}]}
from functools import lru_cache as _lru
CAV3 = os.path.join(CACHE, "fonts/Caveat.woff"); MK3 = os.path.join(CACHE, "fonts/Marker.woff")
PAPER3 = (251, 248, 241); GRID3 = (226, 233, 244); INK3 = (33, 35, 45); BLUE3 = (38, 92, 210); GREEN3 = (22, 150, 84)
RED3 = (222, 52, 42); GRAY3 = (125, 122, 118); HL3 = (255, 224, 90); COIN3 = (255, 205, 60); IGB3 = (0, 149, 246)
COL3 = {"ink": INK3, "red": RED3, "green": GREEN3, "blue": BLUE3, "gray": GRAY3}
CAPY3 = 1590

@_lru(None)
def F3(p, s):
    return ImageFont.truetype(p, int(s * 1.22) if (p == CAV3 and s >= 45) else int(s))
def cl3(x): return max(0.0, min(1.0, x))
def P3(fr, a, b): return ease((fr - a) / max(1e-6, b - a))

@_lru(None)
def _wob(pts, seed, amp=2.6, step=6):
    rnd = np.random.default_rng(seed); ph = rnd.random(3) * 6.28; out = []; acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0); n = max(1, int(L / step)); nx, ny = -(y1 - y0) / (L or 1), (x1 - x0) / (L or 1)
        for i in range(n):
            u = i / n; s = acc + u * L
            o = amp * (math.sin(s / 37 + ph[0]) * .6 + math.sin(s / 13 + ph[1]) * .3 + math.sin(s / 71 + ph[2]) * .5)
            out.append((x0 + (x1 - x0) * u + nx * o, y0 + (y1 - y0) * u + ny * o))
        acc += L
    out.append(pts[-1]); return tuple(out)

def stroke3(d, pts, p, w=7, col=INK3, seed=1, amp=2.6):
    if p <= 0 or len(pts) < 2: return None
    q = _wob(tuple((float(a), float(b)) for a, b in pts), seed, amp); q = q[:max(2, int(len(q) * cl3(p)))]
    d.line(q, fill=col, width=int(w), joint="curve")
    for x, y in (q[0], q[-1]): d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=col)
    return q[-1]

def circ3(cx, cy, rx, ry=None, turns=1.06, n=48):
    ry = ry or rx
    return [(cx + rx * math.cos(math.radians(-100 + 360 * turns * i / n)), cy + ry * math.sin(math.radians(-100 + 360 * turns * i / n))) for i in range(n + 1)]

def arrow3(d, x0, y0, x1, y1, p, w=8, col=INK3, seed=3, head=28):
    stroke3(d, [(x0, y0), (x1, y1)], p / 0.8 if p < 0.8 else 1, w, col, seed)
    if p > 0.8:
        a = math.atan2(y1 - y0, x1 - x0); h = head * cl3((p - 0.8) / 0.2)
        for s in (1, -1): stroke3(d, [(x1, y1), (x1 - h * math.cos(a + s * .5), y1 - h * math.sin(a + s * .5))], 1, w, col, seed + 5 + s)

def text3(im, x, y, s, font, col, p, anchor="mm"):
    if p <= 0 or not s: return
    x, y = int(round(x)), int(round(y)); d = ImageDraw.Draw(im); b = d.textbbox((x, y), s, font=font, anchor=anchor)
    w, h = b[2] - b[0] + 4, b[3] - b[1] + 4
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).text((x - b[0], y - b[1]), s, font=font, fill=255, anchor=anchor)
    if p < 1: ImageDraw.Draw(m).rectangle((int(w * cl3(p)), 0, w, h), fill=0)
    im.paste(col + (255,) if im.mode == "RGBA" else col, (b[0], b[1]), m)

def hl3(im, x, y, s, font, p, col=HL3, anchor="mm"):
    if p <= 0 or not s: return
    d = ImageDraw.Draw(im); b = d.textbbox((int(x), int(y)), s, font=font, anchor=anchor); x1 = b[0] - 14 + (b[2] - b[0] + 28) * cl3(p)
    d.polygon([(b[0] - 14, b[1] + 4), (x1, b[1] - 2), (x1, b[3] + 8), (b[0] - 14, b[3] + 12)], fill=col)

def fitf3(path, size, s, maxw):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); s0 = size; f = F3(path, s0)
    while d.textlength(s, font=f) > maxw and s0 > 22: s0 *= 0.92; f = F3(path, s0)
    return f

def coin3(im, cx, cy, r, label, p, seed=4):
    if p <= 0: return
    s = max(0.01, back(p)); rr = r * s; d = ImageDraw.Draw(im)
    d.ellipse((cx - rr + 5, cy - rr + 7, cx + rr + 5, cy + rr + 7), fill=(225, 220, 208)); d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=COIN3)
    stroke3(d, circ3(cx, cy, rr), 1, max(3, int(6 * s)), INK3, seed, 1.2)
    if label and s > .3: text3(im, cx, cy + 2, label, F3(MK3, max(10, int(r * .7 * s))), INK3, 1)

def stick3(d, cx, cy, sc, p, col=INK3, seed=7):
    stroke3(d, circ3(cx, cy - 150 * sc, 48 * sc), P3(p, 0, .3), 7, col, seed, 1.2)
    stroke3(d, [(cx, cy - 102 * sc), (cx, cy + 20 * sc)], P3(p, .3, .5), 7, col, seed + 1)
    stroke3(d, [(cx - 70 * sc, cy - 40 * sc), (cx, cy - 70 * sc), (cx + 70 * sc, cy - 40 * sc)], P3(p, .5, .7), 7, col, seed + 2)
    stroke3(d, [(cx - 55 * sc, cy + 120 * sc), (cx, cy + 20 * sc), (cx + 55 * sc, cy + 120 * sc)], P3(p, .7, 1), 7, col, seed + 3)
    if p > .3:
        for dx in (-16, 16): d.ellipse((cx + dx * sc - 5, cy - 160 * sc - 5, cx + dx * sc + 5, cy - 160 * sc + 5), fill=col)

# ---------- fotos tipo polaroid
LAYOUTS3 = {   # fotos: (cx, cy, w, h, rot) · zona de notas: (cx, y0, y1, ancho)
    "uno":       {"photos": [(540, 600, 700, 500, -3)], "notes": (540, 960, 1340, 880)},
    "dos":       {"photos": [(330, 560, 450, 340, -5), (770, 960, 380, 300, 6)], "notes": (295, 880, 1340, 450)},
    "foto_lado": {"photos": [(320, 700, 420, 560, -4)], "notes": (785, 360, 1340, 450)},
    "sin_foto":  {"photos": [], "notes": (540, 330, 1340, 880)},
}

class Hibrido:
    def __init__(self, data, total, folder):
        self.d, self.total, self.folder, self.L = data, total, folder, data["lines"]
        self.cache = {}
        bg = Image.new("RGB", (W, H), PAPER3); d = ImageDraw.Draw(bg)
        for x in range(0, W, 54): d.line((x, 0, x, H), fill=GRID3, width=2)
        for y in range(0, H, 54): d.line((0, y, W, y), fill=GRID3, width=2)
        d.line((92, 0, 92, H), fill=(240, 180, 175), width=3)
        self.bg = bg
        last = []
        for l in self.L:                       # líneas sin fotos heredan las de la anterior
            if l.get("layout") != "sin_foto" and not l.get("photos") and l.get("type") != "follow": l["photos"] = last
            last = l.get("photos") or last
            if not l.get("layout"): l["layout"] = "dos" if len(l.get("photos") or []) >= 2 else ("uno" if l.get("photos") else "sin_foto")
        self._words()
        self.hook = data.get("hook")
        if not self.hook:                  # sin gancho explícito: usa la cifra o el texto más destacado de la 1.ª frase
            ns = self.L[0].get("notes") or []
            big = next((n.get("prefix", "") + fmt_num(n["value"]) + n.get("suffix", "") for n in ns if n.get("type") == "numero"), None) \
                or next((n["text"] for n in ns if n.get("type") in ("texto", "rodear") and n.get("text")), None)
            if big: self.hook = {"top": data.get("company", ""), "big": big, "bottom": "¿Cómo pudo pasar?"}

    def _words(self):
        self.ws = []
        for li, l in enumerate(self.L):
            ws = l["show"].split(); wts = [len(re.sub(r"\W", "", w)) + 2 for w in ws]; tot, acc = sum(wts), l["start"]
            for w, wt in zip(ws, wts):
                dd = (l["end"] - l["start"]) * wt / tot; self.ws.append({"w": w, "s": acc, "e": acc + dd, "line": li}); acc += dd
        self.chunks, cur = [], []
        for w in self.ws:
            if cur and (cur[-1]["line"] != w["line"] or len(cur) >= 3 or re.search(r"[.,?!:]$", cur[-1]["w"])):
                self.chunks.append(cur); cur = []
            cur.append(w)
        self.chunks.append(cur)

    def src_img(self, src, w, h):
        k = (src, w, h)
        if k not in self.cache:
            im = Image.open(os.path.join(self.folder, src)).convert("RGB"); s = max(w * 1.12 / im.width, h * 1.12 / im.height)
            im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
            self.cache[k] = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.1)).enhance(1.05)
        return self.cache[k]

    def polaroid(self, im, ph, slot, p, kb, seed):
        if p <= 0: return
        cx, cy, w, h, rot = slot; big = self.src_img(ph["src"], w, h); z = 1 + 0.08 * kb
        cw, ch = int(w * 1.12 / z), int(h * 1.12 / z); fx, fy = ph.get("focus", [0.5, 0.45])
        x = min(max(cw / 2, fx * big.width), big.width - cw / 2); y = min(max(ch / 2, fy * big.height), big.height - ch / 2)
        pic = big.crop((int(x - cw / 2), int(y - ch / 2), int(x + cw / 2), int(y + ch / 2))).resize((w, h), Image.BILINEAR)
        m = 22; lab = 64 if ph.get("label") else 26
        card = Image.new("RGBA", (w + 2 * m, h + 2 * m + lab), (255, 255, 255, 255)); card.paste(pic, (m, m))
        if ph.get("label"): text3(card, (w + 2 * m) // 2, h + m + 10 + lab // 2, ph["label"], fitf3(MK3, 44, ph["label"], w), INK3, 1)
        card.alpha_composite(Image.new("RGBA", (190, 54), (240, 226, 160, 200)), ((w + 2 * m) // 2 - 95, 0))
        s = back(p); c = card.rotate(rot + (1 - ease(p)) * 8, expand=True, resample=Image.BICUBIC)
        c = c.resize((max(2, int(c.width * s)), max(2, int(c.height * s))), Image.BICUBIC)
        sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.putalpha(c.getchannel("A").point(lambda v: int(v * 0.3)))
        X, Y = int(cx - c.width / 2), int(cy - c.height / 2 + (1 - ease(p)) * -120)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (X + 10, Y + 16)); im.alpha_composite(c, (X, Y))

    # ---------- anotaciones
    HEIGHTS = {"texto": {"s": 90, "m": 115, "l": 165}, "numero": 220, "rodear": 240, "check": 110, "contrato": 400, "bola": 340,
               "monedas": 290, "munecos": 290, "web": 250, "grafica": 460, "precio": 160}

    def note_h(self, n):
        h = self.HEIGHTS.get(n.get("type"), 0)
        return h.get(n.get("size", "m"), 100) if isinstance(h, dict) else h

    def draw_notes(self, im, d, li, fr):
        l = self.L[li]; lay = LAYOUTS3[l["layout"]]; ncx, y0, y1, nw = lay["notes"]
        notes = l.get("notes") or []; flow = [n for n in notes if self.note_h(n)]
        tot = sum(self.note_h(n) for n in flow); k = min(1.0, (y1 - y0) / tot) if tot else 1
        gap = ((y1 - y0) - tot * k) / (len(flow) + 1) if flow else 0; gap = min(gap, 60)
        y = y0 + max(0, ((y1 - y0) - tot * k - gap * (len(flow) - 1)) / 2) if flow else y0
        slots = lay["photos"]; n_ph = len(l.get("photos") or [])
        for i, n in enumerate(notes):
            at = float(n.get("at", 0.15 + 0.6 * i / max(1, len(notes)))); p = P3(fr, at, min(1.0, at + 0.22))
            col = COL3.get(n.get("color", "ink"), INK3); typ = n.get("type"); seed = 1000 + li * 50 + i * 7
            h = self.note_h(n) * k
            cy = y + h / 2
            if typ == "texto":
                size = {"s": 64, "m": 86, "l": 124}.get(n.get("size", "m"), 86) * k
                font = MK3 if n.get("font", "marker") == "marker" else CAV3
                f = fitf3(font, size, n["text"], nw)
                if n.get("highlight"): hl3(im, ncx, cy, n["text"], f, p)
                text3(im, ncx, cy, n["text"], f, col, p)
                if n.get("underline"):
                    tw = ImageDraw.Draw(im).textlength(n["text"], font=f); stroke3(d, [(ncx - tw / 2, cy + f.size * .55), (ncx + tw / 2, cy + f.size * .55 - 4)], P3(fr, at + .15, at + .3), 6, col, seed)
            elif typ == "numero":
                if p > 0:
                    v = float(n["value"]) * ease(min(1, (fr - at) / 0.3)); s = n.get("prefix", "") + fmt_num(v) + n.get("suffix", "")
                    text3(im, ncx, cy - 20 * k, s, fitf3(MK3, 160 * k, n.get("prefix", "") + fmt_num(n["value"]) + n.get("suffix", ""), nw), COL3.get(n.get("color", "red")), 1)
                if n.get("label"): text3(im, ncx, cy + 72 * k, n["label"], fitf3(CAV3, 58 * k, n["label"], nw), INK3, P3(fr, at + .1, at + .25))
            elif typ == "rodear":
                f = fitf3(MK3, 96 * k, n["text"], nw - 60); text3(im, ncx, cy, n["text"], f, INK3, p)
                tw = ImageDraw.Draw(im).textlength(n["text"], font=f)
                stroke3(d, circ3(ncx, cy, tw / 2 + 45, 70 * k), P3(fr, at + .08, at + .25), 8, COL3.get(n.get("color", "red")), seed, 1.5)
            elif typ == "check":
                f = fitf3(MK3, 70 * k, n["text"], nw - 90); tw = ImageDraw.Draw(im).textlength(n["text"], font=f)
                text3(im, ncx - 40, cy, n["text"], f, col if n.get("color") else GREEN3, p)
                x = ncx - 40 + tw / 2 + 25; ok = n.get("ok", True)
                if ok: stroke3(d, [(x, cy), (x + 24, cy + 28), (x + 70, cy - 30)], P3(fr, at + .12, at + .25), 10, GREEN3, seed)
                else: stroke3(d, [(x, cy - 25), (x + 50, cy + 25)], P3(fr, at + .12, at + .2), 10, RED3, seed); stroke3(d, [(x + 50, cy - 25), (x, cy + 25)], P3(fr, at + .2, at + .28), 10, RED3, seed + 1)
            elif typ == "contrato":
                w2, h2 = 240 * k, 280 * k; x0, yy = ncx - w2 / 2, cy - h / 2 + 10
                stroke3(d, [(x0, yy), (x0 + w2, yy), (x0 + w2, yy + h2), (x0, yy + h2), (x0, yy)], p, 7, INK3, seed, 1.6)
                for j in range(5): stroke3(d, [(x0 + 28, yy + 45 * k + j * 38 * k), (x0 + w2 - 28 - (j % 2) * 40, yy + 45 * k + j * 38 * k)], P3(fr, at + .05 + j * .02, at + .12 + j * .02), 5, GRAY3, seed + j + 1)
                stroke3(d, [(x0 + 30 + u * (w2 - 60), yy + h2 - 40 * k + 16 * math.sin(u * 14)) for u in np.linspace(0, 1, 30)], P3(fr, at + .2, at + .3), 6, BLUE3, seed + 9)
                if n.get("text"): text3(im, ncx, yy + h2 + 45 * k, n["text"], fitf3(MK3, 54 * k, n["text"], nw), INK3, P3(fr, at + .25, at + .35))
            elif typ == "bola":
                r = 135 * k; pb = p
                if pb > 0:
                    rr = r * back(pb); d.ellipse((ncx - rr, cy - rr, ncx + rr, cy + rr), fill=(40, 40, 48)); stroke3(d, circ3(ncx, cy, rr), 1, 8, INK3, seed, 1.2)
                if fr > at + .1:
                    text3(im, ncx, cy - 18 * k, n.get("text", ""), fitf3(MK3, 54 * k, n.get("text", ""), r * 1.7), (255, 255, 255), P3(fr, at + .1, at + .2))
                    text3(im, ncx, cy + 48 * k, n.get("label", "DEUDA"), F3(MK3, 44 * k), RED3, P3(fr, at + .15, at + .25))
                for j in range(4): stroke3(d, [(ncx - r - 120 + j * 30, cy - 60 + j * 18), (ncx - r - 95 + j * 30, cy - 32 + j * 18)], P3(fr, at + .2 + j * .03, at + .25 + j * .03), 8, GRAY3, seed + 3 + j)
            elif typ == "monedas":
                bw, bh = 300 * k, 170 * k; bx0, by0 = ncx - bw / 2, cy - bh / 2 + 40 * k
                stroke3(d, [(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh), (bx0, by0)], p, 8, INK3, seed, 1.6)
                text3(im, ncx, by0 + bh / 2, n.get("text", ""), fitf3(MK3, 58 * k, n.get("text", ""), bw - 30), COL3.get(n.get("color", "red")), P3(fr, at + .08, at + .18))
                sx, sy = (slots[0][0], slots[0][1]) if slots and n_ph else (ncx, y0 - 100)
                for j in range(5):
                    q = cl3((fr - at - .12 - j * .07) / .2)
                    if 0 < q < 1: coin3(im, sx + (ncx - sx) * q, sy + (by0 - sy) * q - 120 * math.sin(q * math.pi), 30 * k, n.get("symbol", "$"), 1, seed + 10 + j)
            elif typ == "munecos":
                cnt = int(n.get("n", 3)); sp = min(130, nw / max(1, cnt))
                for j in range(cnt): stick3(d, ncx - sp * (cnt - 1) / 2 + j * sp, cy - 10 * k, 0.55 * k, P3(fr, at + j * .05, at + .12 + j * .05), col if n.get("color") else BLUE3, seed + j * 7)
                if n.get("text"): text3(im, ncx, cy + 105 * k, n["text"], fitf3(CAV3, 56 * k, n["text"], nw), col if n.get("color") else BLUE3, P3(fr, at + .1, at + .25))
            elif typ == "web":
                bw, bh = min(nw, 380) * k, 190 * k; bx0, by0 = ncx - bw / 2, cy - bh / 2
                stroke3(d, [(bx0, by0), (bx0 + bw, by0), (bx0 + bw, by0 + bh), (bx0, by0 + bh), (bx0, by0)], p, 7, INK3, seed, 1.6)
                stroke3(d, [(bx0, by0 + 40 * k), (bx0 + bw, by0 + 40 * k)], p, 5, INK3, seed + 1)
                if p > .5:
                    for j in range(3): d.ellipse((bx0 + 16 + j * 24, by0 + 12 * k, bx0 + 30 + j * 24, by0 + 26 * k), fill=GRAY3)
                text3(im, ncx, by0 + bh * .6, n.get("text", ""), fitf3(CAV3, 52 * k, n.get("text", ""), bw - 30), GRAY3, P3(fr, at + .08, at + .18))
                if n.get("tachar", True):
                    stroke3(d, [(ncx - 90 * k, cy - 70 * k), (ncx + 90 * k, cy + 80 * k)], P3(fr, at + .2, at + .28), 13, RED3, seed + 2)
                    stroke3(d, [(ncx + 90 * k, cy - 70 * k), (ncx - 90 * k, cy + 80 * k)], P3(fr, at + .28, at + .36), 13, RED3, seed + 3)
            elif typ == "grafica":
                vals = [float(v) for v in n["values"]]; labs = n.get("labels", [""] * len(vals)); vm = max(vals) or 1
                gw, gh = min(nw, 760), 330 * k; gx0, gy1 = ncx - gw / 2, cy + gh / 2 - 30 * k
                stroke3(d, [(gx0, gy1 - gh), (gx0, gy1), (gx0 + gw, gy1)], p, 7, INK3, seed)
                bw = gw / len(vals) * 0.55
                for j, (v, lb) in enumerate(zip(vals, labs)):
                    q = P3(fr, at + .1 + j * .08, at + .3 + j * .08); bx = gx0 + gw * (j + .5) / len(vals); bh = (gh - 40) * v / vm * q
                    c = COL3.get((n.get("colors") or [None] * len(vals))[j] or n.get("color", "blue"), BLUE3)
                    if bh > 8: d.rectangle((bx - bw / 2, gy1 - bh, bx + bw / 2, gy1 - 4), fill=c + (255,) if im.mode == "RGBA" else c)
                    bh = max(bh, 6 * q)
                    stroke3(d, [(bx - bw / 2, gy1), (bx - bw / 2, gy1 - bh), (bx + bw / 2, gy1 - bh), (bx + bw / 2, gy1)], 1 if bh > 2 else 0, 5, INK3, seed + 3 + j, 1.2)
                    text3(im, bx, gy1 + 40 * k, str(lb), fitf3(CAV3, 46 * k, str(lb), gw / len(vals)), INK3, P3(fr, at + .1, at + .2))
                    if q > .9 and n.get("values_text"): text3(im, bx, gy1 - bh - 30 * k, str(n["values_text"][j]), fitf3(MK3, 42 * k, str(n["values_text"][j]), gw / len(vals)), c, 1)
            elif typ == "precio":
                tx, ty, tw2 = ncx, cy, 170 * k
                stroke3(d, [(tx - tw2, ty - 50 * k), (tx + tw2 - 40, ty - 50 * k), (tx + tw2, ty), (tx + tw2 - 40, ty + 50 * k), (tx - tw2, ty + 50 * k), (tx - tw2, ty - 50 * k)], p, 7, INK3, seed, 1.6)
                text3(im, tx - 15, ty, n.get("text", "$$$"), fitf3(MK3, 56 * k, n.get("text", "$$$"), tw2 * 1.6), GREEN3, P3(fr, at + .1, at + .2))
            # superpuestas a las fotos (no ocupan sitio)
            elif typ == "tachar" and n_ph:
                cx, cyp, w, hh, _ = slots[min(int(n.get("foto", 0)), len(slots) - 1)]; r = min(w, hh) * .42
                stroke3(d, [(cx - r, cyp - r), (cx + r, cyp + r)], P3(fr, at, at + .1), 15, RED3, seed); stroke3(d, [(cx + r, cyp - r), (cx - r, cyp + r)], P3(fr, at + .1, at + .2), 15, RED3, seed + 1)
            elif typ == "sello" and n_ph:
                cx, cyp, w, hh, _ = slots[min(int(n.get("foto", 0)), len(slots) - 1)]
                Reel.stamp(self, im, n["text"].upper(), at * self._dur, fr * self._dur, cx, cyp, 120, -9)
            elif typ == "flecha" and n_ph >= 2:
                a, b = slots[0], slots[1]
                arrow3(d, a[0] + a[2] * .3, a[1] + a[3] * .55, b[0] - b[2] * .35, b[1] - b[3] * .45, p, 9, COL3.get(n.get("color", "green")), seed, 30)
                if n.get("text"):
                    mx = (a[0] + b[0]) / 2 + 150; my = (a[1] + a[3] * .5 + b[1] - b[3] * .5) / 2
                    text3(im, mx, my, n["text"], fitf3(CAV3, 56, n["text"], 300), COL3.get(n.get("color", "green")), P3(fr, at + .15, at + .3))
            elif typ == "rodear_foto" and n_ph:
                cx, cyp, w, hh, _ = slots[min(int(n.get("foto", 0)), len(slots) - 1)]
                fx, fy = n.get("donde", [0.5, 0.5]); px, py = cx - w / 2 + fx * w, cyp - hh / 2 + fy * hh
                stroke3(d, circ3(px, py, w * .18, hh * .16), p, 9, RED3, seed, 1.5)
            if self.note_h(n): y += h + gap
            # (layout comment) notas de flujo se apilan de arriba abajo en la zona de notas

    def stamp(self, im, text, t_in, lt, cx, cy, size=120, rot=-9): return Reel.stamp(self, im, text, t_in, lt, cx, cy, size, rot)
    def layer(self): return Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def comp(self, im, lay, alpha=1.0, scale=1.0, center=(540, 700)): Reel.comp(self, im, lay, alpha, scale, center)

    # ---------- cierre
    def follow(self, im, d, fr, dur):
        t = fr * dur * 1.45            # animación comprimida: el cierre dura ~2,5 s
        text3(im, 540, 360, "¿TE HA GUSTADO?", F3(MK3, 76), INK3, cl3(t / 0.35))
        X0, X1, Y0, Y1 = 150, 930, 480, 960; pc = cl3((t - 0.15) / 0.3)
        if pc > 0:
            s = back(pc); card = self.layer(); cd = ImageDraw.Draw(card)
            cd.rounded_rectangle((X0, Y0, X1, Y1), radius=40, fill=(255, 255, 255, 255))
            ax, ay, ar = X0 + 130, Y0 + 135, 85
            for j in range(14):
                c = tuple(int(u + (v - u) * j / 13) for u, v in zip((254, 196, 21), (216, 26, 136)))
                cd.arc((ax - ar - 14, ay - ar - 14, ax + ar + 14, ay + ar + 14), j * 360 / 14 - 90, (j + 1) * 360 / 14 - 88, fill=c, width=9)
            cd.ellipse((ax - ar, ay - ar, ax + ar, ay + ar), fill=RED2)
            if self.d.get("avatar", "texto") == "texto":       # logo de @cerro.en.rojo: "CERRÓ" con fosforito + "EN ROJO" en rojo, sobre papel
                cd.ellipse((ax - ar, ay - ar, ax + ar, ay + ar), fill=PAPER3 + (255,))
                f1, f2 = F3(MK3, 34), F3(MK3, 36)
                w1 = cd.textlength("CERRÓ", font=f1); cd.rectangle((ax - w1 / 2 - 6, ay - 42, ax + w1 / 2 + 6, ay - 8), fill=HL3 + (255,))
                cd.text((ax, ay - 25), "CERRÓ", font=f1, fill=INK3 + (255,), anchor="mm")
                cd.text((ax, ay + 18), "EN ROJO", font=f2, fill=RED3 + (255,), anchor="mm")
                cd.line([(ax - 50, ay + 48), (ax - 15, ay + 54), (ax + 15, ay + 50), (ax + 52, ay + 62)], fill=RED3 + (255,), width=5)
            elif self.d.get("avatar") == "velas":
                for j, (dx, dy, hh) in enumerate([(-50, -40, 36), (-17, -16, 30), (17, 10, 36), (50, 34, 30)]):
                    cx, cy = ax + dx, ay + dy; cd.line((cx, cy - hh / 2 - 16, cx, cy + hh / 2 + 16), fill=(255, 255, 255), width=4)
                    cd.rectangle((cx - 11, cy - hh / 2, cx + 11, cy + hh / 2), fill=(255, 255, 255))
            else:
                cd.text((ax, ay - 20), self.d["avatar"][0], font=F(FB, 38), fill=(255, 255, 255), anchor="mm"); cd.text((ax, ay + 22), self.d["avatar"][1], font=F(FB, 38), fill=YEL, anchor="mm")
            cd.text((X0 + 260, Y0 + 95), self.d.get("handle", "cerro.en.rojo"), font=F(FB, 50), fill=INK3, anchor="lm")
            cd.text((X0 + 260, Y0 + 155), self.d.get("tagline", ["La bolsa mundial", "explicada en 30 segundos"])[0], font=F(FX, 36), fill=(110, 110, 110), anchor="lm")
            cd.text((X0 + 260, Y0 + 200), self.d.get("tagline", ["La bolsa mundial", "explicada en 30 segundos"])[1], font=F(FX, 36), fill=(110, 110, 110), anchor="lm")
            tap = 1.6; bx0, by0, bx1, by1 = X0 + 50, Y0 + 330, X1 - 50, Y0 + 430
            if t < tap:
                cd.rounded_rectangle((bx0, by0, bx1, by1), radius=22, fill=IGB3); cd.text(((bx0 + bx1) // 2, (by0 + by1) // 2), "Seguir", font=F(FB, 48), fill=(255, 255, 255), anchor="mm")
            else:
                cd.rounded_rectangle((bx0, by0, bx1, by1), radius=22, fill=(239, 239, 239)); cx, cy = (bx0 + bx1) // 2 + 30, (by0 + by1) // 2
                cd.text((cx, cy), "Siguiendo", font=F(FB, 48), fill=INK3, anchor="mm"); x = cx - 190; q = ease((t - tap) / 0.25)
                if q > 0: cd.line([(x, cy), (x + 16, cy + 17), (x + 46, cy - 18)][:2 if q < .4 else 3], fill=GREEN3, width=9, joint="curve")
            sc = s * (1 - 0.06 * max(0, 1 - abs(t - tap) / 0.12)); card = card.resize((int(W * sc), int(H * sc)), Image.BICUBIC)
            ox, oy = int((X0 + X1) / 2 * (1 - sc)), int((Y0 + Y1) / 2 * (1 - sc))
            lay = self.layer(); lay.alpha_composite(card, (ox, oy))
            shd = self.layer(); shd.putalpha(lay.getchannel("A").point(lambda v: int(v * .25)))
            im.alpha_composite(shd.filter(ImageFilter.GaussianBlur(14)), (8, 14)); im.alpha_composite(lay)
            stroke3(d, [(X0 - 12, Y0 - 12), (X1 + 12, Y0 - 12), (X1 + 12, Y1 + 12), (X0 - 12, Y1 + 12), (X0 - 12, Y0 - 12)], cl3((t - .4) / .5), 6, INK3, 700, 1.6)
            curve = [((1 - u) ** 2 * 960 + 2 * (1 - u) * u * 1010 + u * u * 860, (1 - u) ** 2 * 1260 + 2 * (1 - u) * u * 1060 + u * u * (by1 + 20)) for u in np.linspace(0, 1, 30)]
            stroke3(d, curve, cl3((t - .6) / .5), 8, INK3, 701)
            text3(im, 900, 1310, "¡pulsa aquí!", F3(CAV3, 66), BLUE3, cl3((t - .8) / .4))
            if 1.0 < t < tap + 0.7:
                u = ease((t - 1.0) / (tap - 1.05)); fx = int(1000 + (bx1 - 80 - 1000) * u); fy = int(1500 + ((by0 + by1) // 2 - 1500) * u)
                l3 = self.layer(); d3 = ImageDraw.Draw(l3); al = int(255 * min(1, (tap + 0.7 - t) / 0.25))
                if t >= tap:
                    rr = 40 + 120 * ease((t - tap) / .45); d3.ellipse((fx - rr, fy - rr, fx + rr, fy + rr), outline=(38, 92, 210, max(0, int(220 * (1 - (t - tap) / .7)))), width=8)
                d3.ellipse((fx - 38, fy - 38, fx + 38, fy + 38), fill=(255, 255, 255, int(al * .85)), outline=(20, 20, 20, al), width=5)
                im.alpha_composite(l3)
        _fin = self.d.get("cierre", "MAÑANA, MÁS BOLSA"); hl3(im, 540, 1150, _fin, F3(MK3, 70), cl3((t - 2.1) / .4)); text3(im, 540, 1150, _fin, F3(MK3, 70), RED3, cl3((t - 2.1) / .4))

    def end_of(self, i): return self.L[i + 1]["start"] if i + 1 < len(self.L) else self.total

    def page(self, i, t):
        im = self.bg.copy().convert("RGBA"); d = ImageDraw.Draw(im); l = self.L[i]
        dur = max(0.3, self.end_of(i) - l["start"]); fr = (t - l["start"]) / dur; self._dur = dur
        if l.get("type") == "follow":
            self.follow(im, d, fr, dur); return im
        slots = LAYOUTS3[l["layout"]]["photos"]
        for j, (ph, slot) in enumerate(zip(l.get("photos") or [], slots)):
            self.polaroid(im, ph, slot, P3(fr, j * .18, j * .18 + .15), fr, 900 + j)
        self.draw_notes(im, d, i, fr)
        _bw = max(120, int(d.textlength(self.d.get("brand", "CERRÓ EN ROJO"), font=F(FX, 32)) / 2) + 28); d.rounded_rectangle((W // 2 - _bw, 110, W // 2 + _bw, 166), radius=28, fill=RED2)
        d.text((W // 2, 138), self.d.get("brand", "CERRÓ EN ROJO"), font=F(FX, 32), fill=(255, 255, 255), anchor="mm")
        return im

    def captions(self, im, t):
        ch = None
        for c in self.chunks:
            if c[0]["s"] - 0.03 <= t: ch = c
        if ch is None or t > ch[-1]["e"] + 0.35 or self.L[ch[0]["line"]].get("type") == "follow": return
        d = ImageDraw.Draw(im); txts = [w["w"].upper() for w in ch]; f = F(FB, 84)
        while d.textlength(" ".join(txts), font=f) > 820 and f.size > 40: f = F(FB, f.size - 4)
        x = 540 - d.textlength(" ".join(txts), font=f) / 2
        for w, s in zip(ch, txts):
            on = w["s"] <= t < w["e"] + 0.05
            d.text((x, CAPY3), s, font=f, fill=YEL if on else (255, 255, 255), anchor="lm", stroke_width=9, stroke_fill=(15, 15, 15))
            x += d.textlength(s + " ", font=f)

    def render(self, t):
        i = max(k for k, l in enumerate(self.L) if l["start"] - 0.28 <= t or k == 0)
        q = (t - (self.L[i]["start"] - 0.28)) / 0.3
        if i > 0 and q < 1:
            e = ease(q); a = self.page(i - 1, self.L[i]["start"] - 0.29); b = self.page(i, max(t, self.L[i]["start"]))
            im = Image.new("RGBA", (W, H)); im.alpha_composite(a, (int(-W * e), 0)); im.alpha_composite(b, (int(W * (1 - e)), 0))
        else:
            im = self.page(i, t)
        d = ImageDraw.Draw(im); d.rectangle((0, H - 14, int(W * t / self.total), H), fill=RED2)
        u = 0.0 if t < 1.3 else ease((t - 1.3) / 0.32)       # la portada-gancho sube y destapa la primera página
        if u < 1 and self.hook:
            im = im.copy(); im.alpha_composite(self.hook_img(), (0, int(-H * u)))
        if u > 0.5 or not self.hook: self.captions(im, t)
        return im.convert("RGB")

    # ---------- gancho: portada que se lee entera desde el fotograma 0
    def hook_img(self):
        if getattr(self, "_hook", None) is not None: return self._hook
        h = self.hook; im = self.bg.copy().convert("RGBA"); d = ImageDraw.Draw(im)
        _bw = max(120, int(d.textlength(self.d.get("brand", "CERRÓ EN ROJO"), font=F(FX, 32)) / 2) + 28); d.rounded_rectangle((W // 2 - _bw, 110, W // 2 + _bw, 166), radius=28, fill=RED2)
        d.text((W // 2, 138), self.d.get("brand", "CERRÓ EN ROJO"), font=F(FX, 32), fill=(255, 255, 255), anchor="mm")
        ph = (self.L[0].get("photos") or [None])[0]
        if ph: self.polaroid(im, ph, (540, 1250, 500, 350, -4), 1.0, 0.0, 950)
        def lines2(txt, path, size, maxw):
            f = F3(path, size); words = txt.split()
            if ImageDraw.Draw(im).textlength(txt, font=f) <= maxw or len(words) < 2: return [txt], fitf3(path, size, txt, maxw)
            best = min(range(1, len(words)), key=lambda k: abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
            a, b = " ".join(words[:best]), " ".join(words[best:])
            return [a, b], fitf3(path, size, max(a, b, key=len), maxw)
        y = 450
        if h.get("top"):
            ls, f = lines2(h["top"], MK3, 66, 900)
            for k, x in enumerate(ls): text3(im, 540, y + k * (f.size + 10), x, f, INK3, 1)
            y += len(ls) * (f.size + 10) + 40
        big = h.get("big", ""); fb = fitf3(MK3, 200, big, 940); yb = y + fb.size * 0.6
        col = COL3.get(h.get("color", "red"), RED3)
        hl3(im, 540, yb, big, fb, 1); text3(im, 540, yb, big, fb, col, 1)
        y = yb + fb.size * 0.7 + 30
        if h.get("bottom"):
            ls, f = lines2(h["bottom"], CAV3, 74, 900)
            for k, x in enumerate(ls): text3(im, 540, y + k * (f.size + 6), x, f, BLUE3, 1)
            yy = y + len(ls) * (f.size + 6) - 10
            stroke3(d, [(250, yy), (830, yy - 6)], 1, 6, BLUE3, 960)
        self._hook = im; return im

def main_v3(folder, data):
    import soundfile as sf
    L = data["lines"]
    if L and "ígueme" in L[-1].get("say", "") and len(L) > 1: L.pop()
    fs = data.get("follow_say") or FOLLOW_SAY_BOLSA; say = fs[sum(map(ord, data.get("slug", "x"))) % len(fs)]
    L.append({"say": say, "show": say, "type": "follow", "layout": "sin_foto"})
    for l in L: assert l.get("say") and l.get("show"), f"línea sin say/show: {l}"
    for l in L:
        for ph in l.get("photos") or []: assert os.path.exists(os.path.join(folder, ph["src"])), f"falta la foto {ph['src']}"
    voz = data.get("voz", "es-ES-AlvaroNeural")          # voz por defecto de @cerro.en.rojo: Álvaro (neuronal)
    try:
        total = make_voice_edge(folder, L, voz, data.get("voz_rate", "+10%")) if voz != "kokoro" else make_voice(folder, L)
    except Exception as e:
        print("AVISO: falló la voz neuronal, uso Kokoro:", e); total = make_voice(folder, L)
    a, sr = sf.read(os.path.join(folder, "voice.wav")); sf.write(os.path.join(folder, "voice.wav"), np.concatenate([a, np.zeros(int(0.8 * sr))]), sr); total += 0.8
    v = Hibrido(data, total, folder); print(f"duración {total:.1f}s")
    if total > 33: print(f"AVISO: dura {total:.1f} s; el objetivo es 20-30 s: ACORTA EL GUION y vuelve a generar")
    if "--stills" in sys.argv:
        os.makedirs(os.path.join(folder, "stills"), exist_ok=True)
        v.render(0).save(os.path.join(folder, "stills", "gancho.png"))
        for i in range(len(L)): v.render(max(2.0, v.end_of(i) - 0.4)).save(os.path.join(folder, "stills", f"{i:02d}.png"))
        print("stills en", os.path.join(folder, "stills")); return
    make_music(folder, total, [{"start": l["start"], "card": {"i": i}} for i, l in enumerate(L)], seed=sum(map(ord, data.get("slug", "x"))))
    out = os.path.join(folder, "reel.mp4")
    fc = ("[1:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3,aresample=44100,asplit=2[v][key];"
          "[2:a]volume=0.24,lowpass=f=9000[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    p = subprocess.Popen([ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(folder, "voice.wav"), "-i", os.path.join(folder, "music.wav"), "-filter_complex", fc,
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(total * FPS)): p.stdin.write(v.render(fr / FPS).tobytes())
    p.stdin.close(); p.wait()
    assert p.returncode == 0 and os.path.getsize(out) > 100_000, "falló ffmpeg"
    print("OK", out, os.path.getsize(out) // 1024, "KB")


# ================================================================== FORMATO 4 · TERMINAL (POR DEFECTO de @cerro.en.rojo)
# Pantalla de trading: cinta de cotizaciones, titulares de última hora, gráfica de precios REALES que se dibuja en directo,
# cifras tipo marcador, barras comparativas y cierre "Sígueme, dale a like y guarda el vídeo". El código va incrustado y se
# ejecuta como módulo aparte para no mezclar nombres con los formatos antiguos.
TERMINAL_SRC = r'''"""Formato TERMINAL de @cerro.en.rojo: estética de pantalla de trading (fondo oscuro, cinta de cotizaciones, gráfica de precios
REALES que se dibuja en directo, titulares de última hora, cifras tipo marcador) + voz neuronal + subtítulos.
   python3 terminal.py <carpeta con script.json> [--stills]"""
import json, math, os, re, subprocess, sys
_st = "--stills" in sys.argv
import make_reel as M
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

W, H, FPS = 1080, 1920, 30
BG = (9, 12, 18); PANEL = (17, 22, 32); GRIDC = (28, 36, 50); TXT = (235, 240, 248); DIM = (120, 132, 150)
GRN = (33, 208, 122); RED = (255, 64, 64); AMB = (255, 196, 0); WHITE = (255, 255, 255)
MONO = os.path.join(M.CACHE, "fonts/Mono.woff"); FB, FX = M.FB, M.FX
F = M.F
def cl(x): return max(0.0, min(1.0, x))
E, B = M.ease, M.back
def P(fr, a, b): return E((fr - a) / max(1e-6, b - a))

def fit(text, path, size, maxw):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); s = size
    while d.textlength(text, font=F(path, int(s))) > maxw and s > 20: s *= 0.93
    return F(path, int(s))

def glow(im, draw_fn, col, r=18, alpha=0.7):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(lay), col + (255,))
    g = lay.filter(ImageFilter.GaussianBlur(r)); g.putalpha(g.getchannel("A").point(lambda v: int(v * alpha)))
    im.alpha_composite(g); im.alpha_composite(lay)

class Terminal:
    def __init__(self, data, total, folder):
        self.d, self.L, self.total, self.folder = data, data["lines"], total, folder
        self.cache = {}
        bg = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(bg)
        for x in range(0, W, 60): d.line((x, 0, x, H), fill=GRIDC, width=1)
        for y in range(0, H, 60): d.line((0, y, W, y), fill=GRIDC, width=1)
        v = Image.new("L", (W, H), 0); ImageDraw.Draw(v).ellipse((-300, -200, W + 300, H + 200), fill=255)
        dark = Image.new("RGBA", (W, H), (0, 0, 0, 170)); dark.putalpha(v.point(lambda p: 170 - int(p * 0.66)).filter(ImageFilter.GaussianBlur(120)))
        bg.alpha_composite(dark); self.bg = bg
        self.series = {k: v for k, v in data.get("series", {}).items()}
        self._words()

    def _words(self):
        self.ws = []
        for li, l in enumerate(self.L):
            ws = l["show"].split(); wts = [len(re.sub(r"\W", "", w)) + 2 for w in ws]; tot, acc = sum(wts), l["start"]
            for w, wt in zip(ws, wts):
                dd = (l["end"] - l["start"]) * wt / tot; self.ws.append({"w": w, "s": acc, "e": acc + dd, "line": li}); acc += dd
        self.chunks, cur = [], []
        for w in self.ws:
            if cur and (cur[-1]["line"] != w["line"] or len(cur) >= 3 or re.search(r"[.,?!:]$", cur[-1]["w"])):
                self.chunks.append(cur); cur = []
            cur.append(w)
        self.chunks.append(cur)

    # ---------- piezas fijas
    def ticker(self, im, t):
        d = ImageDraw.Draw(im); d.rectangle((0, 0, W, 92), fill=(5, 7, 11, 255)); d.line((0, 92, W, 92), fill=GRIDC, width=2)
        items = self.d.get("ticker", []); f = F(MONO, 34)
        if items:
            segs = []
            for name, chg in items:
                s1 = f"{name} "; s2 = f"{'+' if chg >= 0 else ''}{chg:.1f}%".replace(".", ",")
                w1, w2 = d.textlength(s1, font=f), d.textlength(s2, font=f); segs.append((s1, s2, chg, w1, w2, w1 + 30 + w2 + 80))
            Lc = sum(sg[5] for sg in segs); x = 30 - (t * 140) % Lc
            while x < W + 50:
                for s1, s2, chg, w1, w2, ww in segs:
                    if x + ww > -10 and x < W + 50:
                        col = GRN if chg >= 0 else RED
                        d.text((x, 46), s1, font=f, fill=TXT, anchor="lm"); x2 = x + w1
                        d.polygon([(x2, 58), (x2 + 22, 58), (x2 + 11, 36)] if chg >= 0 else [(x2, 36), (x2 + 22, 36), (x2 + 11, 58)], fill=col)
                        d.text((x2 + 30, 46), s2, font=f, fill=col, anchor="lm")
                    x += ww
        d.rounded_rectangle((W - 270, 116, W - 30, 166), radius=25, fill=(255, 40, 40, 255))
        d.ellipse((W - 250, 133, W - 234, 149), fill=WHITE if int(t * 2) % 2 == 0 else (255, 160, 160))
        d.text((W - 132, 141), "EN DIRECTO" if self.d.get("tipo", "actualidad") == "actualidad" else "HISTORIA", font=F(FX, 28), fill=WHITE, anchor="mm")
        d.text((40, 141), self.d.get("brand", "CERRÓ EN ROJO"), font=F(FB, 34), fill=TXT, anchor="lm")
        d.rectangle((40, 166, 40 + d.textlength(self.d.get("brand", "CERRÓ EN ROJO"), font=F(FB, 34)), 171), fill=RED)

    def captions(self, im, t):
        ch = None
        for c in self.chunks:
            if c[0]["s"] - 0.03 <= t: ch = c
        if ch is None or t > ch[-1]["e"] + 0.35 or self.L[ch[0]["line"]].get("type") == "follow": return
        d = ImageDraw.Draw(im); txts = [w["w"].upper() for w in ch]; f = F(FB, 80)
        while d.textlength(" ".join(txts), font=f) > 860 and f.size > 40: f = F(FB, f.size - 4)
        x = 540 - d.textlength(" ".join(txts), font=f) / 2
        for w, s in zip(ch, txts):
            on = w["s"] <= t < w["e"] + 0.05
            d.text((x, 1590), s, font=f, fill=AMB if on else WHITE, anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0))
            x += d.textlength(s + " ", font=f)

    def photo(self, src, size):
        k = (src, size)
        if k not in self.cache:
            im = Image.open(os.path.join(self.folder, src)).convert("RGB"); s = max(size[0] / im.width, size[1] / im.height)
            im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
            x0, y0 = (im.width - size[0]) // 2, (im.height - size[1]) // 3
            self.cache[k] = im.crop((x0, y0, x0 + size[0], y0 + size[1]))
        return self.cache[k]

    # ---------- escenas
    def s_titular(self, im, v, lt, dur):
        """Tarjetas de 'última hora' que entran apiladas."""
        heads = v["heads"]; y = 470
        if v.get("photo"):
            ph = self.photo(v["photo"], (900, 420)).copy(); ph = ImageEnhance.Brightness(ph).enhance(0.55)
            a = cl(lt / 0.3); ph.putalpha(int(255 * a)); im.alpha_composite(ph.convert("RGBA") if ph.mode != "RGBA" else ph, (90, 230))
        for i, h in enumerate(heads):
            at = i * dur / max(1, len(heads)) * 0.8; p = B((lt - at) / 0.35)
            if p <= 0: continue
            card = Image.new("RGBA", (920, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
            d.rounded_rectangle((0, 0, 920, 230), radius=22, fill=(244, 246, 250, 255))
            d.rectangle((0, 0, 14, 230), fill=RED)
            d.text((44, 46), h.get("tag", "ÚLTIMA HORA"), font=F(FX, 30), fill=RED, anchor="lm")
            f = fit(h["text"], FB, 64, 840)
            words = h["text"].split(); lines = [h["text"]]
            if d.textlength(h["text"], font=F(FB, 60)) > 840 and len(words) > 2:
                k = len(words) // 2; lines = [" ".join(words[:k]), " ".join(words[k:])]; f = fit(max(lines, key=len), FB, 60, 840)
            for j, ln in enumerate(lines): d.text((44, 120 + j * (f.size + 8) - (len(lines) - 1) * f.size / 2), ln, font=f, fill=(15, 18, 26), anchor="lm")
            rot = (-2.5, 1.8, -1.2)[i % 3]; c = card.rotate(rot, expand=True, resample=Image.BICUBIC)
            s = 0.8 + 0.2 * p; c = c.resize((int(c.width * s), int(c.height * s)), Image.BICUBIC)
            sh = Image.new("RGBA", c.size, (0, 0, 0, 0)); sh.putalpha(c.getchannel("A").point(lambda q: int(q * 0.5)))
            X = int(540 - c.width / 2 + (1 - E((lt - at) / 0.3)) * 700); Y = int(y + i * 250 - c.height / 2 + 115)
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (X + 10, Y + 18)); im.alpha_composite(c, (X, Y))

    def s_grafica(self, im, v, lt, dur):
        """Gráfica de precios reales que se dibuja en directo; la cabeza lleva el precio; el tramo final se marca."""
        ser = self.series[v["serie"]]; ys = np.array(ser["close"], float); n = len(ys)
        x0, x1, y0, y1 = 110, 970, 360, 1240
        lo, hi = ys.min(), ys.max(); pad = (hi - lo) * 0.12; lo -= pad; hi += pad
        gx = lambda i: x0 + (x1 - x0) * i / (n - 1); gy = lambda val: y1 - (y1 - y0) * (val - lo) / (hi - lo)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((60, 230, 1020, 1330), radius=26, fill=PANEL + (235,), outline=GRIDC, width=2)
        d.text((100, 290), v.get("titulo", ser.get("name", "")), font=F(FB, 46), fill=TXT, anchor="lm")
        d.text((980, 290), ser.get("sub", ""), font=F(FX, 28), fill=DIM, anchor="rm")
        for k in range(5):
            yy = y0 + (y1 - y0) * k / 4; val = hi - (hi - lo) * k / 4
            d.line((x0, yy, x1, yy), fill=GRIDC, width=1); d.text((x1 + 6, yy), f"{val:,.0f}".replace(",", "."), font=F(MONO, 22), fill=DIM, anchor="lm")
        labs = ser.get("labels", [])
        for i, lab in labs: d.text((gx(i), y1 + 36), lab, font=F(MONO, 24), fill=DIM, anchor="mm")
        p = cl((lt - 0.15) / max(0.5, dur * v.get("draw", 0.7)))
        k = max(2, int(p * (n - 1)) + 1); pts = [(gx(i), gy(ys[i])) for i in range(k)]
        if p < 1 and k < n:   # interpolar la cabeza
            fpart = p * (n - 1) - (k - 1); xi = gx(k - 1) + (gx(k) - gx(k - 1)) * fpart; yi = ys[k - 1] + (ys[k] - ys[k - 1]) * fpart
            pts.append((xi, gy(yi))); cur = yi
        else: cur = ys[k - 1]
        up = cur >= ys[0]; col = GRN if up else RED
        poly = pts + [(pts[-1][0], y1), (pts[0][0], y1)]
        area = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(area).polygon(poly, fill=col + (60,)); im.alpha_composite(area)
        glow(im, lambda dd, c: dd.line(pts, fill=c, width=7, joint="curve"), col, 14, 0.8)
        hx, hy = pts[-1]
        d = ImageDraw.Draw(im); r = 13 + 4 * math.sin(lt * 8); d.ellipse((hx - r, hy - r, hx + r, hy + r), fill=col)
        lab = f"{ser.get('pre', '')}{cur:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        f = F(MONO, 36); tw = d.textlength(lab, font=f)
        bx = min(max(hx - tw / 2 - 14, 70), 1010 - tw - 28); by = hy - 82 if hy > 470 else hy + 30
        d.rounded_rectangle((bx, by, bx + tw + 28, by + 54), radius=10, fill=col); d.text((bx + 14, by + 27), lab, font=f, fill=(5, 8, 12), anchor="lm")
        mk = v.get("marca")    # resalta el último tramo (la caída)
        if mk and p >= 1:
            q = E((lt - 0.15 - dur * v.get("draw", 0.7)) / 0.4); i0 = n - 1 - mk.get("dias", 1)
            ax, ay = gx(i0), gy(ys[i0]); bx2, by2 = gx(n - 1), gy(ys[-1])
            d.rounded_rectangle((ax - 26, min(ay, by2) - 30, bx2 + 26, max(ay, by2) + 30), radius=14, outline=RED + (int(255 * q),), width=5)
            t2 = mk["texto"]; f2 = F(FB, int(96 * (0.6 + 0.4 * B(q)))) if q > 0 else None
            if f2: glow(im, lambda dd, c: dd.text((540, 1180 if by2 < 900 else 460), t2, font=f2, fill=c, anchor="mm"), RED, 22, 0.6)

    def s_cifra(self, im, v, lt, dur):
        val = float(v["value"]); p = E((lt - 0.1) / 0.9); cur = val * p
        dec = v.get("dec", 0); s = f"{cur:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        txt = v.get("prefix", "") + s + v.get("suffix", ""); col = {"red": RED, "green": GRN, "amber": AMB}.get(v.get("color", "red"), RED)
        if v.get("photo"):
            ph = self.photo(v["photo"], (520, 520)); m = Image.new("L", (520, 520), 0); ImageDraw.Draw(m).ellipse((0, 0, 519, 519), fill=255)
            a = B(lt / 0.4); sz = max(2, int(520 * a)); im.paste(ph.resize((sz, sz)), (540 - sz // 2, 520 - sz // 2), m.resize((sz, sz)))
            d = ImageDraw.Draw(im); d.ellipse((540 - sz // 2 - 8, 520 - sz // 2 - 8, 540 + sz // 2 + 8, 520 + sz // 2 + 8), outline=col, width=8)
            if v.get("name"): d.rounded_rectangle((540 - 230, 760, 540 + 230, 820), radius=30, fill=PANEL); d.text((540, 790), v["name"], font=fit(v["name"], FX, 34, 430), fill=TXT, anchor="mm")
            cy = 1010
        else: cy = 760
        f = fit(v.get("prefix", "") + f"{val:,.{dec}f}".replace(",", ".") + v.get("suffix", ""), MONO, 190, 960)
        glow(im, lambda dd, c: dd.text((540, cy), txt, font=f, fill=c, anchor="mm"), col, 26, 0.65)
        if v.get("label"):
            d = ImageDraw.Draw(im); d.text((540, cy + f.size * 0.75), v["label"], font=fit(v["label"], FX, 52, 900), fill=TXT, anchor="mm")

    def s_barras(self, im, v, lt, dur):
        items = v["items"]; mx = max(it[1] for it in items); d = ImageDraw.Draw(im)
        d.text((540, 330), v.get("titulo", ""), font=fit(v.get("titulo", ""), FB, 56, 940), fill=TXT, anchor="mm")
        for i, (name, val, txt, colk) in enumerate(items):
            y = 520 + i * 260; q = E((lt - 0.15 - i * 0.25) / 0.7); col = {"red": RED, "green": GRN, "dim": DIM, "amber": AMB}[colk]
            d.text((90, y - 60), name, font=F(FX, 44), fill=TXT, anchor="lm")
            d.rounded_rectangle((90, y, 990, y + 90), radius=16, fill=PANEL)
            wbar = 900 * val / mx * q
            if wbar > 20: d.rounded_rectangle((90, y, 90 + wbar, y + 90), radius=16, fill=col)
            if q > 0.3: d.text((990, y - 60), txt, font=F(MONO, 50), fill=col if colk != "dim" else TXT, anchor="rm")

    def s_follow(self, im, v, lt, dur):
        t = lt * 1.3; d = ImageDraw.Draw(im)
        d.text((540, 400), "¿TE HA SERVIDO?", font=F(FB, 78), fill=TXT, anchor="mm")
        acts = [("like", "DALE A LIKE", RED), ("save", "GUÁRDALO", AMB), ("follow", "SÍGUEME", GRN)]
        for i, (k, label, col) in enumerate(acts):
            at = 0.25 + i * 0.55; p = B((t - at) / 0.35)
            if p <= 0: continue
            cy = 640 + i * 250; cx = 300; on = t > at + 0.35
            r = 85 * p; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PANEL, outline=col, width=6)
            if k == "like":
                s = 1.3 * p; pts = [(cx + 46 * s * math.sin(a) ** 3 * 1.0, cy - (37 * s * math.cos(a) - 14 * s * math.cos(2 * a) - 6 * s * math.cos(3 * a) - 2 * s * math.cos(4 * a)) * 1.0 - 6) for a in np.linspace(0, 2 * math.pi, 60)]
                d.polygon(pts, fill=col if on else None, outline=col); d.line(pts + [pts[0]], fill=col, width=6)
            elif k == "save":
                s = p; bw, bh = 52 * s, 70 * s; poly = [(cx - bw / 2, cy - bh / 2), (cx + bw / 2, cy - bh / 2), (cx + bw / 2, cy + bh / 2), (cx, cy + bh / 4), (cx - bw / 2, cy + bh / 2)]
                d.polygon(poly, fill=col if on else None, outline=col); d.line(poly + [poly[0]], fill=col, width=6)
            else:
                s = p; d.ellipse((cx - 22 * s, cy - 44 * s, cx + 22 * s, cy), outline=col, width=6, fill=col if on else None)
                d.arc((cx - 44 * s, cy + 2, cx + 44 * s, cy + 80 * s), 180, 360, fill=col, width=6)
            d.text((cx + 130, cy), label, font=F(FB, 66), fill=col if on else TXT, anchor="lm")
            if on and t < at + 0.8:
                q = (t - at - 0.35) / 0.45
                for j in range(8):
                    a = j * math.pi / 4; r0, r1 = 100 + 40 * q, 130 + 60 * q
                    d.line((cx + r0 * math.cos(a), cy + r0 * math.sin(a), cx + r1 * math.cos(a), cy + r1 * math.sin(a)), fill=col, width=6)
        d.text((540, 1530), "Información divulgativa. No es recomendación de inversión.", font=F(FX, 28), fill=DIM, anchor="mm")
        f = F(FB, 54); h = "@" + self.d.get("handle", "cerro.en.rojo"); p = B((t - 2.0) / 0.4)
        if p > 0:
            tw = d.textlength(h, font=f); d.rounded_rectangle((540 - tw / 2 - 40, 1360, 540 + tw / 2 + 40, 1450), radius=45, fill=RED)
            d.text((540, 1405), h, font=f, fill=WHITE, anchor="mm")

    # ---------- gancho (fotograma 0)
    def hook(self, im, t):
        h = self.d["hook"]; lay = self.bg.copy(); self.ticker(lay, t); d = ImageDraw.Draw(lay)
        d.text((540, 470), h["top"].upper(), font=fit(h["top"].upper(), FB, 70, 940), fill=TXT, anchor="mm")
        f = fit(h["big"], MONO, 230, 980); col = RED if h.get("color", "red") == "red" else GRN
        glow(lay, lambda dd, c: dd.text((540, 760), h["big"], font=f, fill=c, anchor="mm"), col, 30, 0.75)
        d = ImageDraw.Draw(lay); d.text((540, 1010), h["bottom"], font=fit(h["bottom"], FX, 64, 940), fill=AMB, anchor="mm")
        if h.get("photo"):
            ph = self.photo(h["photo"], (300, 300)); m = Image.new("L", (300, 300), 0); ImageDraw.Draw(m).ellipse((0, 0, 299, 299), fill=255)
            lay.paste(ph, (390, 1100), m); d.ellipse((382, 1092, 698, 1408), outline=col, width=8)
        return lay

    def render(self, t):
        i = max(k for k, l in enumerate(self.L) if l["start"] - 0.15 <= t or k == 0); l = self.L[i]
        end = self.L[i + 1]["start"] if i + 1 < len(self.L) else self.total; dur = max(0.4, end - l["start"]); lt = max(0.0, t - l["start"])
        im = self.bg.copy(); v = l.get("v", {"type": "follow"}) if l.get("type") != "follow" else {"type": "follow"}
        getattr(self, "s_" + v["type"])(im, v, lt, dur)
        k = (t - (l["start"] - 0.15)) / 0.15
        if i > 0 and k < 1:   # flash de corte
            fl = Image.new("RGBA", (W, H), (255, 255, 255, int(120 * (1 - k)))); im.alpha_composite(fl)
        self.ticker(im, t)
        u = 0.0 if t < 1.3 else E((t - 1.3) / 0.25)
        if u < 1 and self.d.get("hook"):
            hk = self.hook(im, t); hk.putalpha(int(255 * (1 - u))); im.alpha_composite(hk)
        if u > 0.5: self.captions(im, t)
        d = ImageDraw.Draw(im); d.rectangle((0, H - 12, int(W * t / self.total), H), fill=RED)
        return im.convert("RGB")

def main():
    folder = sys.argv[1]; data = json.load(open(os.path.join(folder, "script.json")))
    L = data["lines"]; say = data.get("follow_say", "Sígueme, dale a like y guarda el vídeo.")
    L.append({"say": say, "show": say, "type": "follow"})
    import soundfile as sf
    total = M.make_voice_edge(folder, L, data.get("voz", "es-ES-AlvaroNeural"), data.get("voz_rate", "+12%"))
    a, sr = sf.read(os.path.join(folder, "voice.wav")); sf.write(os.path.join(folder, "voice.wav"), np.concatenate([a, np.zeros(int(1.0 * sr))]), sr); total += 1.0
    v = Terminal(data, total, folder); print(f"duración {total:.1f}s")
    if _st:
        os.makedirs(os.path.join(folder, "stills"), exist_ok=True); v.render(0).save(os.path.join(folder, "stills", "gancho.png"))
        for i, l in enumerate(L):
            end = L[i + 1]["start"] if i + 1 < len(L) else total
            v.render(max(1.8, end - 0.3)).save(os.path.join(folder, "stills", f"{i:02d}.png"))
        return
    M.make_music(folder, total, [{"start": l["start"], "card": {"i": i}} for i, l in enumerate(L)], bpm=110, seed=11)
    out = os.path.join(folder, "reel.mp4")
    fc = ("[1:a]highpass=f=80,acompressor=threshold=-18dB:ratio=3,aresample=44100,asplit=2[v][key];"
          "[2:a]volume=0.22,lowpass=f=9000[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=300[md];"
          "[v][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]")
    p = subprocess.Popen([M.ffmpeg_bin(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", os.path.join(folder, "voice.wav"), "-i", os.path.join(folder, "music.wav"), "-filter_complex", fc,
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for fr in range(int(total * FPS)): p.stdin.write(v.render(fr / FPS).tobytes())
    p.stdin.close(); p.wait(); print("OK", out)

'''

def main_v4(folder, data):
    import types
    sys.modules.setdefault("make_reel", sys.modules[__name__])
    mod = types.ModuleType("terminal_fmt"); exec(compile(TERMINAL_SRC, "terminal_fmt", "exec"), mod.__dict__)
    mod.main()

def precios(symbol, desde=None, hasta=None, intervalo="1d", rango=None):
    """Descarga cierres reales de Yahoo Finance y devuelve una serie lista para script.json["series"]."""
    import urllib.request, datetime as dt
    q = f"interval={intervalo}"
    if rango: q += f"&range={rango}"
    else:
        p1 = int(dt.datetime.fromisoformat(desde).replace(tzinfo=dt.timezone.utc).timestamp())
        p2 = int(dt.datetime.fromisoformat(hasta).replace(tzinfo=dt.timezone.utc).timestamp()) if hasta else int(dt.datetime.now(dt.timezone.utc).timestamp())
        q += f"&period1={p1}&period2={p2}"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.request.quote(symbol)}?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    r = json.load(urllib.request.urlopen(req, timeout=40))["chart"]["result"][0]
    pairs = [(dt.datetime.fromtimestamp(t, dt.timezone.utc).date(), c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if c]
    mes = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    n = len(pairs); labels = []
    years = pairs[-1][0].year - pairs[0][0].year
    step = max(1, n // 6)
    for i in range(0, n, step):
        d0 = pairs[i][0]; labels.append([i, str(d0.year) if years >= 3 else f"{mes[d0.month - 1]}" + (f" {str(d0.year)[2:]}" if years >= 1 else "")])
    return {"name": symbol, "sub": "", "pre": "", "close": [round(c, 2) for _, c in pairs], "labels": labels,
            "desde": str(pairs[0][0]), "hasta": str(pairs[-1][0]), "ultimo": round(pairs[-1][1], 2),
            "penultimo": round(pairs[-2][1], 2) if n > 1 else None, "max": round(max(c for _, c in pairs), 2), "min": round(min(c for _, c in pairs), 2)}

def main():
    if sys.argv[1] == "buscar":          # python3 make_reel.py buscar "texto"
        for r in commons_search(" ".join(sys.argv[2:])): print(json.dumps(r, ensure_ascii=False))
        return
    if sys.argv[1] == "bajar":           # python3 make_reel.py bajar "File:..." carpeta/img/x.jpg "autor" "licencia"
        ok = commons_download(sys.argv[2], sys.argv[3], os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[3]))), "credits.json"),
                              {"author": sys.argv[4] if len(sys.argv) > 4 else "", "license": sys.argv[5] if len(sys.argv) > 5 else ""})
        print("OK" if ok else "FALLO"); return
    if sys.argv[1] == "precios":         # python3 make_reel.py precios GOOGL [--rango 6mo | --desde 1928-01-01 --hasta 1932-12-31] [--intervalo 1d|1wk|1mo]
        a = sys.argv[2:]; sym = a[0]; opt = {a[i].lstrip("-"): a[i + 1] for i in range(1, len(a) - 1, 2)}
        print(json.dumps(precios(sym, opt.get("desde"), opt.get("hasta"), opt.get("intervalo", "1d"), opt.get("rango") if "desde" not in opt else None), ensure_ascii=False))
        return
    folder = sys.argv[1]; stills = "--stills" in sys.argv
    data = json.load(open(os.path.join(folder, "script.json")))
    if data.get("formato") == "terminal":
        return main_v4(folder, data)
    if data.get("formato") == "hibrido" or any(l.get("notes") or l.get("layout") or l.get("photos") for l in data["lines"]):
        return main_v3(folder, data)
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
