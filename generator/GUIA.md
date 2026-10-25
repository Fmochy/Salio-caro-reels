# Salió caro — guía del reel diario

Cuenta de Instagram **@salio.caro** ("Salió caro | Errores de marcas"): cada día un reel de ~30–40 s
sobre una decisión de una empresa conocida que le salió cara. Público: España, curiosos de negocios.
Voz en off sintética (Kokoro, voz `em_alex`), fondo oscuro, subtítulos grandes, una tarjeta animada por frase.

## 1. Elegir el caso

- Lee `casos_publicados.json` (raíz del repo). **Nunca repitas empresa + decisión** ya publicada.
- Elige casos **famosos y bien documentados**, con una cifra clara de coste (dinero perdido, cuota, valor, clientes).
- Varía sector y país semana a semana (tecnología, consumo, automoción, moda, aerolíneas, banca, comida, España/Europa/EEUU/Asia).
- Ideas de partida (si no están ya publicadas): New Coke, Kodak y la cámara digital, Nokia y el iPhone, BlackBerry,
  Yahoo rechazando comprar Google, Quibi, Juicero, WeWork, Segway, Google+, Microsoft Zune, Windows Phone,
  Toys "R" Us, Sears, Pan Am, Concorde, MySpace, Vine, Blockbuster y Netflix (ya publicado),
  Gap logo 2010, Tropicana envase 2009, Crystal Pepsi, Colgate lasaña,
  Nintendo Virtual Boy, Sony Betamax, Netflix–Qwikster (ya hay carrusel,
  evita hasta que lo permita el log), Amazon Fire Phone y Google Glass (ya publicados en la cuenta: evitar).

## 2. Investigar (obligatorio)

- Verifica **cada cifra y fecha con al menos 2 fuentes fiables** (prensa económica, Wikipedia con citas, informes de la empresa).
- Si un dato es dudoso o varía entre fuentes, usa "unos", "más de", "casi" o quítalo. **Nunca inventes.**
- Guarda las URLs en `sources` del script.json.
- Nada de acusaciones penales sin condena, ni datos de personas privadas.

## 3. Escribir `script.json`

Estructura (mira `ejemplo/script.json`, el caso Blockbuster, como referencia de tono y ritmo):

```json
{
 "slug": "kodak-camara-digital",
 "company": "Kodak",
 "tag": "Kodak · 1975",
 "caption": "…",
 "sources": ["https://…", "https://…"],
 "lines": [ { "say": "…", "show": "…", "red": ["palabra"], "card": {…} | "same", "stamp": "…", "badge": "…" } ]
}
```

- `say`: lo que lee la voz. **Números y años escritos con letras** ("cincuenta millones", "dos mil diez").
- `show`: lo mismo para subtítulos, con cifras ("50 millones", "2010"). Misma puntuación que `say`.
- `red`: palabras de `show` (tal cual, con su puntuación) que se resaltan en rojo. 1–2 por frase.
- `card`: tarjeta visual de la frase, o `"same"` para mantener la anterior. La primera frase necesita tarjeta.
- `stamp` (opcional): sello rojo grande sobre la tarjeta ("RECHAZADO", "QUIEBRA", "RETIRADO"). 1–3 palabras.
- `badge` (opcional): etiqueta roja corta ("×6.000", "−40%").

Tipos de tarjeta:

| type | campos | uso |
|---|---|---|
| `money` | `value` (número), `prefix` ("$") o `suffix` (" €"), `label`, `unit`, `color` ("red"/"white") | cifras con contador animado (también usuarios, clientes: sin prefijo) |
| `year` | `year`, `pills` (hasta 2: `{"text", "color":"red"}`) | situar en el tiempo |
| `place` | `title`, `subtitle` | ciudad / sede / lugar |
| `versus` | `a_name`, `a_label`, `b_name`, `b_label`, `b_ratio` (0–1, tamaño de B respecto a A) | comparar dos fuerzas |
| `text` | `lines` (2–3 palabras cortas; la última sale en rojo) | la lección: casi siempre `["Salió", "caro."]` |
| `follow` | — | cierre "Sígueme" |

Reglas de guion:

- **8–11 frases, 85–110 palabras en total** (≈30–40 s). Frases cortas, castellano de España, tono directo de contar una historia.
- **Frase 1 = gancho**: la decisión y el coste con una cifra, sin introducción ("Kodak inventó la cámara digital en 1975. Y la guardó en un cajón.").
- Contexto → decisión → consecuencia con cifra → dato final que impacte.
- Penúltima frase: "A {empresa}, {la decisión} le salió muy caro." con tarjeta `text` ["Salió","caro."].
- Última frase siempre: "Sígueme, y cada día te cuento un caso nuevo." con tarjeta `follow`.
- Nada de emojis en las frases. Sin palabras en inglés si hay equivalente.

Caption (campo `caption`): 1ª línea = el gancho (se ve antes del "más"), 2–3 frases de contexto, una pregunta
para comentarios con 👇, y 4–6 hashtags (#negocios #marketing #emprendimiento + 1–3 del caso).

## 4. Generar y revisar

```bash
bash generator/setup.sh
python3 generator/make_reel.py casos/AAAA-MM-DD-slug --stills   # revisa los PNG con la herramienta Read
python3 generator/make_reel.py casos/AAAA-MM-DD-slug            # genera reel.mp4
```

Revisa los stills: texto cortado, solapes, cifras mal formateadas. Corrige el script.json y repite.
Duración ideal 28–42 s; si pasa de 45 s, recorta frases.
