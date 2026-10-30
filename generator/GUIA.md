# Cerró en Rojo (antes Salió caro) — guía de los reels diarios

# 🖥️ FORMATO "TERMINAL" (desde el 30-oct-2026, OBLIGATORIO para todos los reels de @cerro.en.rojo)

Sustituye al formato híbrido/cuaderno (secciones 3, 3b y 3c ya NO se usan). Estética de pantalla de trading: fondo oscuro con
rejilla, cinta de cotizaciones arriba, sello CERRÓ EN ROJO + pastilla "EN DIRECTO" (actualidad) o "HISTORIA", titulares de
última hora, **gráfica de precios REALES que se dibuja en directo**, cifras tipo marcador, barras comparativas, voz de Álvaro,
subtítulos karaoke amarillos, y cierre automático "Sígueme, dale a like y guarda el vídeo" con iconos animados + aviso legal
(no escribas tú esa línea).

**script.json** (`"formato": "terminal"`):
- `tipo`: "historia" (11:30) o "actualidad" (19:30, noticias de hoy).
- `hook`: {"top": quién/qué (≤ 5 palabras), "big": cifra brutal (≤ 11 caracteres: "-482.000 M$", "-22,6 %", "-89 %"),
  "bottom": el giro (≤ 6 palabras), "color": "red"|"green", "photo": "img/x.jpg" (opcional, sale en círculo)}.
- `ticker`: 5–8 pares [nombre, %] REALES (actualidad: los % de hoy a la hora de hacer el vídeo, de fuentes fiables: la empresa, Nasdaq,
  S&P 500, Dow, Ibex/DAX ya cerrados y 2–4 valores que se mueven hoy). En historia: los índices/valores de aquel día histórico.
- `series`: {"clave": serie} con datos REALES de `python3 generator/make_reel.py precios SIMBOLO --rango 6mo` (actualidad) o
  `--desde AAAA-MM-DD --hasta AAAA-MM-DD --intervalo 1wk|1mo` (historia: "^GSPC" S&P 500 desde 1927, "^DJI", "^IXIC" Nasdaq,
  "^N225" Nikkei, "^GDAXI" DAX, "^IBEX", acciones "AAPL", "NVDA", "BTC-USD"…). Pega el JSON que devuelve y rellena "name"
  ("Alphabet (GOOGL)"), "sub" ("6 meses · cierre diario") y "pre" ("$", "" para índices). NUNCA inventes cifras de la gráfica.
- `lines`: 4–6 frases (20–30 s) con `say`, `show` y `v` (la escena):

| v.type | campos | uso |
|---|---|---|
| `titular` | `heads`: [{"tag": "ÚLTIMA HORA", "text": "≤ 7 palabras"}] (1–3), `photo` opcional (arriba, oscurecida) | 1.ª frase (la noticia) y última (la pregunta: tag "LA GRAN PREGUNTA") |
| `grafica` | `serie`, `titulo`, `draw` (0.5–0.8: parte de la frase en que se dibuja), `marca` {"dias": N, "texto": "-12,6 %"} | la escena estrella: siempre una por reel |
| `cifra` | `value`, `dec`, `prefix`, `suffix`, `label`, `color` red/green/amber, `photo` + `name` (cara del CEO/personaje) | cifras clave con contador |
| `barras` | `titulo`, `items`: [[nombre, valor, "texto", "red"/"green"/"dim"/"amber"], …] (2–3) | comparaciones (récords, antes/después) |

Reglas: la `marca` de la gráfica debe coincidir con los datos (calcula el % con los cierres de la serie). Los titulares son
genéricos ("Alphabet se desploma en bolsa"), nunca atribuidos a un medio. Fotos: caras de CEOs/personajes y sedes (Commons).
Revisa los stills (incluido gancho.png): nada cortado ni solapado.

**Caption (SEO):** 1.ª línea palabras clave + gancho + 📉/📈; 3 líneas 👉 con las cifras; pregunta para comentar;
"Síguenos para entender la bolsa cada día, dale a like y guárdalo 📌"; "Información divulgativa. No es recomendación de inversión.";
5 hashtags (#bolsa + #wallstreet o #inversion + 3 del tema).

**Ejemplo real (actualidad, 25 s):**

```json
{
 "formato": "terminal",
 "slug": "google-terminal",
 "tipo": "actualidad",
 "hook": {
  "top": "Google perdió ayer",
  "big": "-482.000 M$",
  "bottom": "en un solo día",
  "color": "red",
  "photo": "img/googleplex.jpg"
 },
 "ticker": [
  [
   "GOOGL",
   -12.6
  ],
  [
   "NASDAQ",
   -1.4
  ],
  [
   "S&P 500",
   -0.3
  ],
  [
   "DOW",
   -0.3
  ],
  [
   "LLY",
   6.0
  ],
  [
   "DASH",
   5.6
  ]
 ],
 "series": {
  "googl": {
   "name": "Alphabet (GOOGL)",
   "sub": "6 meses · cierre diario",
   "pre": "$",
   "close": [
    "...127 cierres diarios reales, salidos de: python3 generator/make_reel.py precios GOOGL --rango 6mo ..."
   ],
   "labels": [
    [
     1,
     "may"
    ],
    [
     21,
     "jun"
    ],
    [
     42,
     "jul"
    ],
    [
     64,
     "ago"
    ],
    [
     85,
     "sep"
    ],
    [
     106,
     "oct"
    ]
   ]
  }
 },
 "lines": [
  {
   "say": "Google acaba de vivir su peor día en bolsa: perdió cuatrocientos ochenta y dos mil millones de dólares en una sola sesión.",
   "show": "Google acaba de vivir su peor día en bolsa: perdió 482.000 millones de dólares en una sola sesión.",
   "v": {
    "type": "titular",
    "photo": "img/googleplex.jpg",
    "heads": [
     {
      "text": "Alphabet se desploma en bolsa"
     },
     {
      "text": "Pierde 482.000 millones en un día"
     }
    ]
   }
  },
  {
   "say": "Mira la gráfica: venía aguantando, y ayer se hundió casi un trece por ciento de golpe.",
   "show": "Mira la gráfica: venía aguantando, y ayer se hundió casi un 13 % de golpe.",
   "v": {
    "type": "grafica",
    "serie": "googl",
    "titulo": "Alphabet (GOOGL)",
    "draw": 0.65,
    "marca": {
     "dias": 1,
     "texto": "-12,6 %"
    }
   }
  },
  {
   "say": "¿El motivo? Un gasto récord en inteligencia artificial: más de cincuenta y un mil millones en tres meses.",
   "show": "¿El motivo? Un gasto récord en inteligencia artificial: más de 51.000 millones en 3 meses.",
   "v": {
    "type": "cifra",
    "value": 51.4,
    "dec": 1,
    "suffix": " mil M$",
    "label": "invertidos en IA en un trimestre",
    "color": "amber",
    "photo": "img/pichai.jpg",
    "name": "Sundar Pichai · CEO"
   }
  },
  {
   "say": "Solo Nvidia ha perdido más dinero en un solo día.",
   "show": "Solo Nvidia ha perdido más dinero en un solo día.",
   "v": {
    "type": "barras",
    "titulo": "Mayores caídas en un día (EE. UU.)",
    "items": [
     [
      "Nvidia · ene 2025",
      593,
      "593.000 M$",
      "dim"
     ],
     [
      "Google · ayer",
      482,
      "482.000 M$",
      "red"
     ]
    ]
   }
  },
  {
   "say": "La gran pregunta: ¿le saldrá a cuenta tanta inteligencia artificial?",
   "show": "La gran pregunta: ¿le saldrá a cuenta tanta inteligencia artificial?",
   "v": {
    "type": "titular",
    "heads": [
     {
      "tag": "LA GRAN PREGUNTA",
      "text": "¿Le saldrá a cuenta la IA?"
     }
    ],
    "photo": "img/pichai.jpg"
   }
  }
 ],
 "caption": "(caption con SEO, ver abajo)",
 "alt": "(texto alternativo)"
}
```

---

# ⚠️ CAMBIO DE CANAL (30-oct-2026): LA CUENTA AHORA ES @cerro.en.rojo — ESTA SECCIÓN Y LA DE FORMATO TERMINAL MANDAN SOBRE TODO LO DEMÁS

La cuenta de Instagram se llama ahora **@cerro.en.rojo** ("Cerró en Rojo | Bolsa explicada"): **la bolsa mundial explicada en
30 segundos**: actualidad de los mercados + historia de la bolsa. Metricool sigue siendo la misma marca (blogId 7438016).
Todo lo de "Salió caro / errores de marcas" de las secciones 1, 1b y 9-10 queda OBSOLETO; el formato visual (sección 3c),
la duración (20–30 s), el gancho en el fotograma 0, el SEO y las reglas de créditos siguen igual (el formato visual ahora es TERMINAL, ver arriba).

**Qué toca en cada franja (cambio del 30-oct, decisión del dueño):**
- **Reel de las 11:30 (tarea de la mañana, 9:24) = HISTORIA DE LA BOLSA**, de cualquier país: cracs y burbujas (Crac del 29,
  Lunes Negro de 1987, burbuja puntocom, Lehman 2008, Flash Crash 2010, burbuja de Japón 1989, tulipanes, Mares del Sur, Covid 2020),
  quiebras y fraudes que movieron el mercado (Enron, LTCM, Wirecard, FTX), OPV legendarias (Facebook, Saudi Aramco, Alibaba),
  récords (GameStop, Nvidia, Apple 3 billones), personajes (Buffett, Soros y la libra, Livermore). Ya publicados: Terra/Lycos,
  Bankia OPV, Martinsa-Fadesa: no repetir. Pastilla "HISTORIA" (`"tipo": "historia"`).
- **Reel de las 19:30 (tarea de la tarde, 17:00) = LO MÁS CANDENTE DE LA BOLSA DE HOY.** Busca noticias del MISMO DÍA
  (búsquedas web con la fecha de hoy) y elige el tema más llamativo o curioso: el valor que más sube o se hunde, resultados
  sorprendentes, récords, bancos centrales, petróleo/oro, cripto, una OPV, una cifra rara. Enfoque MUNDIAL. Pastilla "EN DIRECTO"
  (`"tipo": "actualidad"`). **Ojo con la hora:** a las 17:00 de Madrid Europa está a punto de cerrar (17:30) y Wall Street sigue
  abierta hasta las 22:00, así que las cifras de EE. UU. son PROVISIONALES: dilo en la voz y en pantalla ("en lo que va de sesión",
  "a media sesión", "a esta hora") y usa como serie la de los últimos meses (cierres) con `marca` solo si el movimiento de hoy está
  confirmado por 2 fuentes. Nunca presentes como cierre un dato intradía.
- **Si hoy no hay bolsa** (sábado, domingo o festivo en Wall Street), la tarea de la tarde hace "lo más curioso de la semana en
  bolsa" (con datos de cierre del viernes) o, si no hay nada potente, otro reel de historia distinto al de la mañana.

**Rigor (obligatorio):** cada cifra con 2 fuentes fiables (Reuters, Bloomberg, CNBC, Yahoo Finance, FT, WSJ, Expansión, Cinco Días,
web oficial de la empresa). En actualidad di que es de hoy y, si el dato es intradía, dilo ("en lo que va de sesión"); los cierres de Europa ya valen a partir de las 17:30.
**Nunca recomiendes**: nada de "compra", "vende", "oportunidad", "va a subir". Cuenta qué pasó y por qué. La última frase puede ser
una pregunta abierta ("¿Le saldrá a cuenta la IA?"), nunca un consejo. En la última línea añade una nota `texto` pequeña gris
"No es recomendación de inversión" y el caption termina con "Información divulgativa. No es recomendación de inversión."

**Voz:** el generador usa ya por defecto la voz neuronal de **Álvaro** (es-ES-AlvaroNeural); no pongas `voz` en el script.
Sigue escribiendo en `say` las cifras con letras. **Cierre:** no escribas tú la frase de "sígueme"; el generador añade
"Sígueme para entender la bolsa cada día" (o similar) y la tarjeta con @cerro.en.rojo y "MAÑANA, MÁS BOLSA".
**Remate:** ya no hace falta "le salió muy caro": termina con la idea clave o una pregunta abierta.

**Gancho (`hook`):** la cifra más brutal en `big` (≤ 14 letras: "-12 %", "482.000 M$", "-22,6 %"), `top` con quién/qué, `bottom` con
el giro ("en un solo día", "y nadie lo vio venir").

**Fotos (Wikimedia Commons, como siempre):** sede o logo de la empresa, su CEO, la Bolsa de Nueva York (NYSE), Wall Street,
el toro de Wall Street, parqués de bolsa, billetes/lingotes/petróleo; las cifras y curvas mejor con `grafica`, `numero` y `rodear`.
Si no hay fotos útiles, usa `layout` "sin_foto" con gráficas.

**SEO del caption:** primera línea = palabras clave que la gente busca + gancho ("Google se hunde en bolsa: Alphabet pierde
482.000 millones en un día 📉"); 3–4 líneas con 👉 explicando las cifras; una pregunta para comentar; el aviso legal; 5 hashtags
(#bolsa #inversion + 3 del tema: empresa, índice, sector). `alt` con lo mismo en una frase.

**Ejemplo ANTIGUO en formato híbrido (NO lo copies: el formato es TERMINAL, ver el ejemplo de arriba):**

```json
{
 "formato": "hibrido",
 "slug": "google-cae-bolsa",
 "company": "Alphabet",
 "hook": {
  "top": "Google perdió ayer",
  "big": "482.000 M$",
  "bottom": "en un solo día",
  "color": "red"
 },
 "lines": [
  {
   "say": "Ayer Google perdió cuatrocientos ochenta y dos mil millones de dólares en bolsa. En un solo día.",
   "show": "Ayer Google perdió 482.000 millones de dólares en bolsa. En un solo día.",
   "layout": "uno",
   "photos": [
    {
     "src": "img/googleplex.jpg",
     "focus": [
      0.5,
      0.4
     ]
    }
   ],
   "notes": [
    {
     "type": "numero",
     "value": 12,
     "prefix": "-",
     "suffix": " %",
     "label": "su acción, en un día",
     "color": "red",
     "at": 0.35
    }
   ]
  },
  {
   "say": "Es su peor caída desde que salió a bolsa en dos mil cuatro.",
   "show": "Es su peor caída desde que salió a bolsa en 2004.",
   "layout": "foto_lado",
   "photos": [
    {
     "src": "img/pichai.jpg",
     "label": "Sundar Pichai, CEO",
     "focus": [
      0.5,
      0.3
     ]
    }
   ],
   "notes": [
    {
     "type": "rodear",
     "text": "2004",
     "at": 0.6
    },
    {
     "type": "texto",
     "text": "peor día",
     "color": "red",
     "highlight": true,
     "at": 0.4
    }
   ]
  },
  {
   "say": "Y eso que su negocio en la nube se duplicó, hasta los treinta mil millones.",
   "show": "Y eso que su negocio en la nube se duplicó, hasta los 30.000 millones.",
   "layout": "sin_foto",
   "notes": [
    {
     "type": "grafica",
     "values": [
      15.2,
      30.7
     ],
     "labels": [
      "3T 2025",
      "3T 2026"
     ],
     "values_text": [
      "15.200 M$",
      "30.700 M$"
     ],
     "colors": [
      "gray",
      "green"
     ],
     "at": 0.1
    },
    {
     "type": "texto",
     "text": "Google Cloud +103 %",
     "color": "green",
     "highlight": true,
     "at": 0.55
    }
   ]
  },
  {
   "say": "El problema: gastó un récord de más de cincuenta y un mil millones en inteligencia artificial en tres meses.",
   "show": "El problema: gastó un récord de más de 51.000 millones en inteligencia artificial en 3 meses.",
   "layout": "uno",
   "photos": [
    {
     "src": "img/campus.jpg",
     "focus": [
      0.5,
      0.5
     ]
    }
   ],
   "notes": [
    {
     "type": "numero",
     "value": 51400,
     "suffix": " M$",
     "label": "invertidos en IA en 3 meses",
     "color": "red",
     "at": 0.3
    }
   ]
  },
  {
   "say": "Arrastró al Nasdaq, y solo Nvidia ha perdido más en un día.",
   "show": "Arrastró al Nasdaq, y solo Nvidia ha perdido más en un día.",
   "layout": "sin_foto",
   "notes": [
    {
     "type": "texto",
     "text": "Nasdaq -1,4 %",
     "color": "red",
     "highlight": true,
     "at": 0.05
    },
    {
     "type": "grafica",
     "values": [
      593,
      482
     ],
     "labels": [
      "Nvidia 2025",
      "Google ayer"
     ],
     "values_text": [
      "593.000 M$",
      "482.000 M$"
     ],
     "colors": [
      "gray",
      "red"
     ],
     "at": 0.4
    }
   ]
  },
  {
   "say": "La gran pregunta: ¿le saldrá a cuenta tanta inteligencia artificial?",
   "show": "La gran pregunta: ¿le saldrá a cuenta tanta inteligencia artificial?",
   "layout": "uno",
   "photos": [
    {
     "src": "img/googleplex.jpg",
     "focus": [
      0.5,
      0.4
     ]
    }
   ],
   "notes": [
    {
     "type": "texto",
     "text": "¿Le saldrá a cuenta?",
     "size": "l",
     "color": "red",
     "highlight": true,
     "at": 0.4
    },
    {
     "type": "texto",
     "text": "No es recomendación de inversión",
     "size": "s",
     "font": "mano",
     "color": "gray",
     "at": 0.1
    }
   ]
  }
 ],
 "caption": "(ver más abajo: caption de bolsa)",
 "alt": "(texto alternativo)"
}
```

---


Cuenta de Instagram **@salio.caro** ("Salió caro | Errores de marcas"): dos reels al día de **20–30 s** (cambio del 28-oct: los de 40 s no se veían enteros)
sobre una decisión de una empresa conocida que le salió cara. Público: España, curiosos de negocios.
Voz en off sintética (Kokoro, voz `em_alex`). **FORMATO POR DEFECTO DESDE EL 27-OCT: HÍBRIDO (sección 3c)**: fotos reales como polaroids
sobre cuaderno + anotaciones dibujadas a mano. Lo eligió el dueño de la cuenta; úsalo SIEMPRE. (Antes: fotos a pantalla completa, sección 3b, como los
shorts virales del nicho. Solo si no se consiguen fotos se usa el formato antiguo de tarjetas (sección 3).

## 1. Elegir el caso

- Lee `casos_publicados.json` (raíz del repo). **Nunca repitas empresa + decisión** ya publicada.
- Además de lo que diga ese fichero, **ya están publicados** en la cuenta (no repetir): New Coke (20-oct), Nokia y los Lumia/Microsoft (21-oct),
  Xbox One (22-oct), Google Glass (23-oct), Amazon Fire Phone (24-oct), Blockbuster y Netflix (25-oct), Toys R Us y Amazon (26-oct),
  Netflix–Qwikster (carrusel), Spanair (26-oct). Añade al registro los que falten cuando actualices casos_publicados.json.
- **Hay DOS reels al día: 11:30 (tarea de las 9:30, que no escribe en el repo) y 19:30 (tarea de las 17:00).** Por eso, además de
  casos_publicados.json, revisa SIEMPRE en Metricool (getScheduledPosts de los últimos 45 días hasta mañana) los textos de los
  reels ya programados o publicados, y no repitas ninguna empresa + decisión que aparezca ahí. El de la tarde nunca puede repetir el de la mañana.
- Duplicados: cada tarea solo mira SU franja. Si ya hay un reel PENDING a esa hora (11:30 o 19:30) hoy, no dupliques; un reel de
  la otra franja, o ya PUBLISHED, no cuenta.
- **PRIORIDAD ESPAÑA (cambio del 28-oct, los datos lo apoyan: Spanair fue el mejor reel):** al menos 5 de cada 7 casos deben ser de
  **marcas españolas** o de marcas que cualquier español conoce y usa (Zara, Mercadona, El Corte Inglés, Telefónica, Seat, Telepizza,
  Coca-Cola, Apple…). Casos lejanos para el público español (Xbox, Google Glass, Zune…) solo de forma excepcional.
  Ideas españolas (si no están publicadas; verifica todo con fuentes y cuenta solo hechos documentados): Pescanova, la salida a bolsa
  de Bankia, Martinsa-Fadesa, Nueva Rumasa, Air Madrid, Galerías Preciados, Pryca y la fusión con Continente, Fórum Filatélico
  y Afinsa, Seat y el Ibiza/Volkswagen, Chupa Chups, Nocilla, Fotoprix, Terra (publicado 27-oct), Spanair (publicado), Kodak (publicado 27-oct),
  Real Madrid-Florentino y los galácticos (solo cifras), la Ciudad de la Justicia de Madrid, el aeropuerto de Castellón, el Castor, la Expo
  y los Juegos del 92 (costes), Mercadona dejando a marcas fuera de sus lineales.
- Elige casos **famosos y bien documentados**, con una cifra clara de coste (dinero perdido, cuota, valor, clientes).
- Varía sector y país semana a semana (tecnología, consumo, automoción, moda, aerolíneas, banca, comida, España/Europa/EEUU/Asia).
- Ideas de partida (si no están ya publicadas): New Coke, Kodak y la cámara digital, Nokia y el iPhone, BlackBerry,
  Yahoo rechazando comprar Google, Quibi, Juicero, WeWork, Segway, Google+, Microsoft Zune, Windows Phone,
  Toys "R" Us, Sears, Pan Am, Concorde, MySpace, Vine, Blockbuster y Netflix (ya publicado),
  Gap logo 2010, Tropicana envase 2009, Crystal Pepsi, Colgate lasaña,
  Nintendo Virtual Boy, Sony Betamax, Netflix–Qwikster (ya hay carrusel,
  evita hasta que lo permita el log), Amazon Fire Phone y Google Glass (ya publicados en la cuenta: evitar).

## 1b. Ángulos que más funcionan en el nicho (análisis de cuentas top, oct. 2026)

Datos de los shorts más vistos de cuentas de historias de empresas (EN y ES). Úsalos para elegir el ÁNGULO del caso,
no solo la empresa. Reparte la semana entre estos ángulos y no repitas el mismo dos días seguidos:

1. **Rivalidad / "X destrozó a Y"** — el caso contado como una pelea con ganador y perdedor
   ("Cómo Amazon destrozó a Toys R Us": 560 veces la media de su canal). Ej.: Netflix vs Blockbuster, iPhone vs Nokia.
2. **Marca española o muy cercana** — lo local arrasa (el top de una cuenta argentina son marcas de su país).
   Al menos 2 casos por semana de empresas españolas o muy presentes en España (Spanair, Air Madrid, Galerías Preciados,
   Terra, Fagor Electrodomésticos, Pryca/Continente, Tuenti, Chupa Chups, Nocilla, Simago…).
3. **Actualidad con pregunta** — una empresa que está en problemas AHORA ("¿GoPro va a quebrar?": 727 veces la media).
   1 por semana como mucho. Solo con noticias de medios fiables de los últimos 30 días y atribuyendo ("según…").
4. **Lo que no sabías / origen sorprendente** — dueños ocultos, orígenes raros, prohibiciones ("La historia oscura de
   Fanta", "Por qué prohibieron los Tamagotchi", "¿Sabías que esta marca es de…?").
5. **La persona dentro de la historia** — una decisión o anécdota humana concreta dentro de la empresa
   ("Vivió en secreto dentro de un Toys R Us": 27 M). Busca el ejecutivo, empleado o cliente que protagoniza el giro.
6. **"¿Por qué…?" de algo cotidiano** — por qué una marca hace algo que todos vemos ("Por qué los logos son todos iguales": 21 M).

Duración: **20–30 s** (cuenta nueva: hay que conseguir que se vean enteros). Máximo 70 palabras en total.
El título/gancho lleva un verbo fuerte (destrozó, hundió, rechazó, perdió, prohibió) o una pregunta directa.
Nunca afirmes delitos ni atribuyas frases inventadas a personas reales; los casos judiciales, solo con condena firme
y citando la fuente, y mejor evitarlos.

## 2. Investigar (obligatorio)

- Verifica **cada cifra y fecha con al menos 2 fuentes fiables** (prensa económica, Wikipedia con citas, informes de la empresa).
- Si un dato es dudoso o varía entre fuentes, usa "unos", "más de", "casi" o quítalo. **Nunca inventes.**
- Guarda las URLs en `sources` del script.json.
- Nada de acusaciones penales sin condena, ni datos de personas privadas.

## 3. Escribir `script.json`

Estructura (la referencia de tono, ritmo y formato es el **ejemplo de la sección 9**, Toys R Us, inspirado en un short viral del nicho; **no uses `ejemplo/script.json` (Blockbuster) como modelo**, no funcionó):

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

- `say`: lo que lee la voz. **Números y años escritos con letras** ("cincuenta millones", "dos mil diez"). Marcas y palabras inglesas escríbelas normal (Amazon, online, CEO): el generador las pronuncia solo como se dicen en España. Si una marca nueva suena mal, escríbela en `say` como se pronuncia (p. ej. "Tois ar as").
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

- **Ritmo fluido, como alguien contándolo de corrido**: une ideas con comas, "y", "pero", "así que"; evita frases telegráficas de 3–4 palabras seguidas. El generador ya lee los puntos internos como comas.
- **Tono de conversación**, como alguien contándoselo a un amigo: expresiones naturales ("y la gente se vuelve loca", "ojo, que aquí viene lo bueno") y **una pregunta al espectador a mitad del vídeo** ("¿Sabes por cuánto lo vendió?") para retenerlo.
- **4–6 frases, 50–70 palabras en total** (≈20–30 s), cada frase de 15 palabras como mucho. Cuenta solo lo esencial: gancho, giro, cifra, remate. Castellano de España, tono directo.
- **Frase 1 = gancho**: elígelo con el proceso de la sección 5 (3 candidatos con fórmulas distintas, puntuados). Sin introducción.
- Contexto → decisión → consecuencia con cifra → dato final que impacte.
- Penúltima frase: "A {empresa}, {la decisión} le salió muy caro." con tarjeta `text` ["Salió","caro."].
- **Cierre automático:** el generador añade solo la frase final de "sígueme" (con frases naturales que van rotando) y la tarjeta
  animada de perfil con el botón "Seguir" que se pulsa y pasa a "Siguiendo". **No escribas tú la línea de "Sígueme"**: termina el guion
  con la frase de remate ("…le salió muy caro."). Si la escribes, el generador la sustituye.
- Nada de emojis en las frases. Sin palabras en inglés si hay equivalente.

Caption (campo `caption`): sigue la sección 6.

## 3b. Formato con fotos a pantalla completa (ANTIGUO: solo si el 3c falla)

Es el estilo de los virales del nicho: imagen real a pantalla completa que cambia cada ~2 s, portada-gancho, cifras
gigantes, rótulos cortos arriba, subtítulos karaoke abajo y final en bucle. El generador lo usa automáticamente cuando
las líneas del script.json llevan `visuals`.

**1) Consigue 6–10 imágenes de Wikimedia Commons** (licencias libres) en `casos/CARPETA/img/`:

```bash
python3 generator/make_reel.py buscar "Toys R Us closing"          # lista ficheros con licencia y autor
python3 generator/make_reel.py bajar "File:Nombre.jpg" casos/CARPETA/img/tienda.jpg "Autor" "CC BY-SA 4.0"
```

Busca en inglés y prueba varias búsquedas: la tienda o sede, el producto, el logo en un edificio, el fundador o CEO,
fábricas, tiendas cerrando, el país o la ciudad. Usa solo licencias CC BY, CC BY-SA, CC0 o dominio público.
Revisa cada imagen con Read antes de usarla (que se vea lo que dices). `bajar` guarda los créditos en `credits.json`.
**Si `buscar` falla o no consigues al menos 4 imágenes útiles, usa el formato híbrido igualmente con `layout` "sin_foto" en las líneas sin imagen.**

**2) En cada línea del script.json añade `visuals`**: lista de 1–4 planos; la frase se reparte entre ellos a partes iguales.
Apunta a un plano cada 2–2,5 s (≈15–20 planos por reel). `src` es la ruta relativa a la carpeta del caso (p. ej. "img/tienda.jpg").

| type | campos | uso |
|---|---|---|
| `title` | `src`, `text1` (caja blanca), `text2` (caja amarilla) | **primer plano obligatorio** (portada-gancho, 3–6 palabras por caja) y también el **último plano** (bucle) |
| `img` | `src`, `focus` [x,y 0–1], `zoom` "in"/"out", `kicker` (rótulo arriba, 1–4 palabras), `stamp` | la mayoría de planos |
| `number` | `src` (fondo), `value`, `prefix`/`suffix`, `label`, `color` "yellow"/"red"/"green" | cifras gigantes con contador |
| `doc` | `src`, `kicker`, `lines` (2 líneas cortas) | demandas, contratos, anuncios oficiales (texto genérico, nunca un titular falso atribuido a un medio) |
| `end` | `src` | "SALIÓ CARO." en la penúltima frase |

Reglas: alterna `zoom` in/out; no repitas la misma imagen en planos seguidos; kickers en mayúsculas cortos ("AÑO 2000",
"¿Y LA DEUDA?"); `red` marca las palabras que se iluminan en amarillo en los subtítulos.
**Créditos/fuentes de las fotos: NUNCA se publican.** Ni en el caption, ni en el primer comentario, ni en el vídeo. Decisión del dueño de la cuenta. `firstCommentText` va SIEMPRE vacío (""). Los créditos solo se quedan en `credits.json` dentro del repo.
Copia la estructura del ejemplo `ejemplo_v2` de la sección 10.

## 3c. Formato HÍBRIDO (POR DEFECTO, úsalo siempre)

Cuaderno de papel cuadriculado; en cada frase caen 1–2 **fotos reales impresas tipo polaroid** (con cinta y zoom lento) y
encima se **dibujan a mano** anotaciones que se trazan mientras habla la voz: años rodeados, flechas, contratos, cifras que
cuentan, tachones, bolas de deuda, monedas, muñequitos… Entre frases la página se desliza. Subtítulos karaoke abajo y cierre
automático con la tarjeta de perfil "Seguir" (no escribas la línea de "Sígueme").

**Imágenes:** igual que en 3b, paso 1 (Wikimedia Commons con `buscar`/`bajar`, revisa cada una con Read). Bastan 5–8.
Elige fotos que se entiendan en pequeño: fachada con logo, producto, fundador/CEO, tienda cerrada, sede.

**Gancho en el fotograma 0 (OBLIGATORIO):** campo `hook` = {"top": "contexto corto (≤ 5 palabras)", "big": "la cifra o frase
más llamativa (≤ 14 letras: \"12.500 M$\", \"800 TIENDAS\")", "bottom": "la duda o el giro (≤ 6 palabras)", "color": red/green/blue}.
Se ve entero desde el primer fotograma 1,3 s (también es la portada) y luego sube y destapa la primera página. Debe decir lo mismo que la
primera frase, que ha de ser corta (≤ 15 palabras). Revisa `stills/gancho.png`.

**script.json:** pon `"formato": "hibrido"` y en cada línea `layout`, `photos` y `notes` (además de say/show/red):

| layout | fotos | dónde van las notas |
|---|---|---|
| `uno` | 1 foto grande arriba | debajo, centradas (la zona más ancha: textos largos, cifras, gráficas) |
| `dos` | 2 fotos en diagonal (arriba-izq. y abajo-dcha.) | columna izquierda abajo (textos cortos ≤ 14 letras) |
| `foto_lado` | 1 foto vertical a la izquierda | columna derecha (textos cortos, contrato, muñecos, web) |
| `sin_foto` | ninguna | toda la página (gráficas, comparaciones) |

`photos`: lista de {"src": "img/x.jpg", "label": "texto bajo la foto (opcional, 1–3 palabras)", "focus": [x, y] (opcional)}.
Si una línea no lleva `photos`, hereda las de la anterior. No repitas la misma foto en más de 2 líneas.

`notes` (2–3 por línea como máximo; `at` = momento de la frase en que aparece, de 0 a 1, sincronízalo con la palabra):

| type | campos | qué dibuja |
|---|---|---|
| `texto` | `text`, `size` s/m/l, `color` ink/red/green/blue/gray, `font` marker/mano, `highlight`, `underline` | texto escrito a mano (fosforito amarillo con highlight) |
| `numero` | `value`, `prefix`, `suffix`, `label`, `color` | cifra grande que cuenta desde 0 |
| `rodear` | `text`, `color` | texto (año, cifra) rodeado con un círculo |
| `check` | `text`, `ok` true/false | texto con ✓ verde (o ✗ roja si ok=false) |
| `contrato` | `text` | documento con firma que se dibuja + pie |
| `bola` | `text`, `label` | bola negra de deuda/carga ("5.000 M$", "DEUDA") |
| `monedas` | `text`, `symbol` | monedas que salen de la foto hacia una caja ("DEUDA", "Amazon"…) |
| `munecos` | `n`, `text`, `color` | n muñequitos de palo (clientes, vendedores, empleados) |
| `web` | `text`, `tachar` | ventana de navegador con la web, tachada por defecto |
| `grafica` | `values`, `labels`, `values_text`, `colors` | barras dibujadas a mano (mejor en `uno` o `sin_foto`) |
| `precio` | `text` | etiqueta de precio |
| `flecha` | `text`, `color` | flecha de la 1.ª foto a la 2.ª (solo `dos`) |
| `tachar` | `foto` (0/1) | X roja enorme sobre la foto |
| `sello` | `text`, `foto` | sello rojo sobre la foto ("QUIEBRA 2017") |
| `rodear_foto` | `donde` [x, y], `foto` | círculo rojo sobre un punto de la foto |

Reglas: la 1.ª línea es el gancho: usa `dos` (empresa contra empresa) o `uno` con un `texto` grande con highlight o un `numero`.
Las cifras importantes van en `numero` o `rodear`. Textos de las notas cortos (≤ 4 palabras; en `dos`/`foto_lado`, ≤ 14 letras).
No uses los caracteres → ≈ ≠ (no están en las fuentes). La penúltima frase (remate "…le salió muy caro.") lleva un `texto`
"SALIÓ CARO" grande en rojo con highlight. Revisa los stills: nada cortado ni encima de otra cosa; si se amontona, quita notas.

Ejemplo completo (Toys R Us en 21 s, el modelo a imitar: fíjate en lo cortas que son las frases):

```json
{
 "formato": "hibrido",
 "slug": "toysrus-amazon",
 "company": "Toys R Us",
 "hook": {
  "top": "Toys R Us pagaba a Amazon",
  "big": "50 M$ al año",
  "bottom": "y Amazon la hundió"
 },
 "lines": [
  {
   "say": "Toys R Us le pagaba a Amazon cincuenta millones al año, y Amazon la hundió.",
   "show": "Toys R Us le pagaba a Amazon 50 millones al año, y Amazon la hundió.",
   "layout": "dos",
   "photos": [
    {
     "src": "img/hialeah.jpg",
     "label": "Toys R Us"
    },
    {
     "src": "img/amz_logo.jpg",
     "label": "Amazon",
     "focus": [
      0.5,
      0.35
     ]
    }
   ],
   "notes": [
    {
     "type": "flecha",
     "at": 0.25
    },
    {
     "type": "texto",
     "text": "50 M$ al año",
     "color": "green",
     "highlight": true,
     "at": 0.3
    }
   ]
  },
  {
   "say": "En dos mil firma diez años vendiendo solo en Amazon, en vez de crear su propia web.",
   "show": "En 2000 firma 10 años vendiendo solo en Amazon, en vez de crear su propia web.",
   "layout": "foto_lado",
   "photos": [
    {
     "src": "img/ts_b.jpg"
    }
   ],
   "notes": [
    {
     "type": "contrato",
     "text": "10 años",
     "at": 0.25
    },
    {
     "type": "web",
     "text": "toysrus.com",
     "at": 0.7
    }
   ]
  },
  {
   "say": "Amazon deja vender juguetes a otros, y Toys R Us pierde años clave.",
   "show": "Amazon deja vender juguetes a otros, y Toys R Us pierde años clave.",
   "layout": "foto_lado",
   "photos": [
    {
     "src": "img/bezos.jpg",
     "label": "Amazon",
     "focus": [
      0.5,
      0.3
     ]
    }
   ],
   "notes": [
    {
     "type": "munecos",
     "n": 3,
     "text": "otros vendedores",
     "at": 0.15
    },
    {
     "type": "texto",
     "text": "años perdidos",
     "color": "red",
     "at": 0.65
    }
   ]
  },
  {
   "say": "En dos mil diecisiete quiebra y cierra ochocientas tiendas.",
   "show": "En 2017 quiebra y cierra 800 tiendas.",
   "layout": "uno",
   "photos": [
    {
     "src": "img/closing6.jpg"
    }
   ],
   "notes": [
    {
     "type": "sello",
     "text": "Quiebra 2017",
     "at": 0.1
    },
    {
     "type": "numero",
     "value": 800,
     "label": "tiendas cerradas",
     "at": 0.45
    }
   ]
  },
  {
   "say": "Regalarle internet a Amazon le salió muy caro.",
   "show": "Regalarle internet a Amazon le salió muy caro.",
   "layout": "dos",
   "photos": [
    {
     "src": "img/hialeah.jpg"
    },
    {
     "src": "img/fc.jpg"
    }
   ],
   "notes": [
    {
     "type": "flecha",
     "text": "internet",
     "color": "ink",
     "at": 0.1
    },
    {
     "type": "texto",
     "text": "SALIÓ CARO",
     "size": "l",
     "color": "red",
     "highlight": true,
     "at": 0.5
    }
   ]
  }
 ],
 "caption": "(ver sección 6)",
 "alt": "(ver sección 6b)"
}
```

## 4. Generar y revisar (después de las secciones 5–7)

```bash
bash generator/setup.sh
python3 generator/make_reel.py casos/AAAA-MM-DD-slug --stills   # revisa los PNG con la herramienta Read
python3 generator/make_reel.py casos/AAAA-MM-DD-slug            # genera reel.mp4
```

Revisa los stills: texto cortado, solapes, cifras mal formateadas. Corrige el script.json y repite.
Duración ideal 20–30 s. **Si el generador avisa de que pasa de 33 s, recorta frases y vuelve a generar** (no publiques un reel de más de 33 s).

## 5. El gancho (método /ig-reel)

El gancho son los primeros 2–3 segundos y decide si el reel se ve. Escribe **3 candidatos con 3 fórmulas distintas**
(no tres versiones de la misma), puntúa cada uno de 0 a 5 con estos criterios y usa el mejor:

1. **Corto**: se dice en menos de 3 s (≤ 14 palabras).
2. **Concreto**: lleva una cifra, un año, un nombre o una marca.
3. **Hay algo en juego**: dinero, quiebra, despidos, cuota, una oportunidad perdida.
4. **Lo importante delante**: el dato fuerte en la primera mitad de la frase, no al final.
5. **Apela al espectador** cuando encaja ("tú", "tu móvil", algo que usa o conoce).

Si ninguno llega a 4/5, el gancho aún no está: busca otro ángulo del caso.

Fórmulas que funcionan para casos de empresas (nº de la lista original de 26). Los ejemplos son solo de estilo: verifica cualquier dato antes de usarlo.

| nº | fórmula | plantilla | ejemplo |
|---|---|---|---|
| 1 | Confesión de coste | {Cifra} es lo que le costó {un error} a {empresa}. | "Treinta y un mil millones: eso llegó a valer Kodak antes de quebrar." |
| 23 | La estadística | {N}% de {grupo} {dato sorprendente}. | "Kodak vendía casi el noventa por ciento de los carretes de Estados Unidos, y aun así quebró." |
| 25 | El resultado ajeno | Hubo una empresa que {logro/fracaso} en {tiempo}. | "Hubo una empresa que levantó mil setecientos millones y cerró en seis meses." |
| 21 | Empezar a mitad de frase | …y ahí fue cuando {el giro}. | "…y entonces Yahoo decidió que Google no le interesaba." |
| 22 | Dicho al revés | {frase conocida, invertida}. | "El cliente no siempre tiene razón: que se lo digan a Coca-Cola en 1985." |
| 3 | Nadie te cuenta | Nadie te cuenta que {verdad incómoda}. | "Nadie te cuenta que la cámara digital la inventó la empresa que arruinó." |
| 24 | La revelación | Esto es {cosa} que {consecuencia}. | "Este es el móvil que hundió a Amazon en el hardware." |
| 26 | El superlativo | El {mayor/más rápido/único} {cosa} es {respuesta}. | "El mayor error de Nokia no fue un móvil: fue una reunión." |
| 14 | La llamada | {Grupo concreto}, esto va por vosotros. | "Si tienes un negocio que va bien, este caso es para ti." |
| 20 | Permiso | No hace falta {lo que todos creen}. | "No hace falta un mal producto para quebrar: basta con ignorar uno bueno." |

Reglas: di el número ("mucho dinero" no es un número); empieza directamente en la frase que normalmente dirías en el
segundo seis; el gancho tiene que cumplir su promesa antes de la mitad del vídeo; si valdría para cualquier otro caso,
no es tu gancho.

Guarda en `script.json` el campo `"hook_formula": "<nº> <nombre>"` y añade también `gancho` y `formula` a la entrada
de `casos_publicados.json`, para que la auditoría semanal sepa qué fórmulas funcionan.

## 6. El caption (método /ig-caption)

El reel ya engancha con su primera frase, así que el caption no compite con él (trabajo "A"):

- **Línea 1 (lo que se ve antes del "más", máx. 125 caracteres)**: la pregunta para comentarios dicha claramente,
  o el dato más llamativo del caso. Nunca empieza con saludo, hashtag ni emoji.
- **Cuerpo**: 2–3 párrafos cortos separados por una línea en blanco, con el contexto y las cifras. Mete aquí 2–3
  **frases que la gente buscaría** escritas con naturalidad (p. ej. "errores de marketing", "fracasos empresariales",
  "historia de Kodak"): la búsqueda de Instagram lee el texto del caption.
- **Una sola petición** (comentar o guardar). Dos peticiones valen lo mismo que ninguna.
- **Hashtags: máximo 5** (Instagram limita a 5 desde dic. 2025), al final, en su propia línea, específicos:
  #negocios #marketing + 1–3 del caso. Nunca #viral, #fyp, #explorepage.
- Sin enlaces. Máximo 1–2 emojis en todo el caption.

## 6b. SEO para llegar lejos (Instagram es también un buscador)

Instagram indexa el **texto del caption**, el **texto alternativo**, el **texto que sale en pantalla** y lo que se **dice en voz** (subtítulos automáticos).
- **Palabra clave principal** = la marca + el hecho (p. ej. "quiebra de Toys R Us", "historia de Kodak"). Debe aparecer en:
  la primera línea del caption, la portada (`title`), la primera frase de la voz y el texto alternativo.
- **Caption**: 2–3 búsquedas naturales en el cuerpo ("historia de empresas", "errores empresariales", "fracasos de marcas",
  "por qué quebró X"). Escritas como frases normales, nunca listas de palabras.
- **Hashtags (máx. 5)**: 1–2 de la marca (#toysrus #amazon) + #negocios #historiaempresarial + 1 temático. Sin hashtags genéricos virales.
- **Texto alternativo**: al programar en Metricool, rellena `mediaAltText` con una frase de 150–250 caracteres que describa el
  vídeo con la palabra clave ("Reel sobre la quiebra de X: cómo… Historia de empresas y errores empresariales.").
- **Portada**: `videoCoverMilliseconds` = 300 (la portada-gancho del primer plano, con la marca bien legible).

## 7. Que no suene a IA (método /ig-human)

Antes de generar, repasa `say`, `show` y `caption`:

- **Quita** rayas largas (—) y cámbialas por comas; comillas tipográficas por rectas; caracteres invisibles.
- **Palabras de relleno prohibidas**: "sumérgete", "en el mundo actual", "en la era digital", "fascinante",
  "crucial", "sin duda", "revolucionario", "un antes y un después", "cabe destacar", "es importante mencionar",
  "descubre", "increíble", "no te lo pierdas", "dale like", "etiqueta a alguien", "el algoritmo".
- **Estructuras que delatan**: "no es solo X, es Y"; listas de tres adjetivos; preguntas de una palabra tipo
  "¿El resultado?"; "en este vídeo te voy a contar"; tres palabras en mayúsculas seguidas. Reescribe esas frases.
- **Que suene dicho en voz alta**: varía la longitud de las frases, usa cifras y nombres concretos, y escribe como
  hablaría una persona de Madrid contándoselo a un amigo. Si una frase no la dirías tú, reescríbela.

## 8. Aprendizajes de la cuenta (lo actualiza la auditoría semanal; tiene prioridad sobre las reglas generales)

<!-- APRENDIZAJES:INICIO -->
Auditoría 26-10-2026 · 6 reels (20–25 oct; 5 con más de 48 h). Muestra pequeña (<7): son tendencias, no reglas firmes.
- Mejores: Nokia 1,7×, Xbox One 1,5× y New Coke 1,0× la mediana (71 visualizaciones), con 5–7 s de visionado medio.
  Peores: Fire Phone 0,2× y Google Glass 0,06×, con 1–3 s. La gente se va en el gancho, no a mitad del vídeo.
- Gancho: marca + lo que estaba en juego en la primera mitad de la frase, con cifra de coste (fórmulas 1, 24 o 26).
  Evita ganchos abstractos sin coste ni tensión ("X no terminó donde empezó", "45 días entre... y una rebaja radical").
- Prioriza marcas que el público español ha usado o bebido (Coca-Cola, Nokia, consolas) frente a gadgets que casi nadie tuvo.
- No encadenes dos casos del mismo sector: tres tecnológicos seguidos (22–24 oct) coincidieron con la caída de alcance.
- Ningún reel tiene compartidos, guardados ni seguidores: termina con un dato final que den ganas de mandar a alguien,
  y en el caption una sola petición, preferiblemente comentar con una pregunta de sí/no.
- Rellena SIEMPRE gancho y formula en casos_publicados.json: sin ellos la auditoría no puede comparar fórmulas.
<!-- APRENDIZAJES:FIN -->

## 9. Ejemplo antiguo de tarjetas (NO lo imites en longitud ni formato: manda la sección 3c)

Inspirado en el short "How Amazon DESTROYED Toys R Us" (1,4 M de visualizaciones, 560 veces la media de su canal).
Fíjate en: gancho paradójico con cifra en la primera frase, rivalidad con un "malo", tono de conversación
("Pero ojo", "Y encima"), pregunta al espectador a mitad ("¿Sabes qué hacía esa deuda?"), una cifra fuerte por tarjeta
y cierre "le salió muy caro". Copia la estructura y el ritmo, nunca los datos.

```json
{
 "slug": "toys-r-us-amazon",
 "company": "Toys R Us",
 "tag": "Toys R Us × Amazon",
 "hook_formula": "1 Confesión de coste + rivalidad",
 "caption": "¿Sabías que Toys R Us le pagaba a Amazon para vender sus juguetes? 👇\n\nEn el año 2000 firmó 10 años de exclusiva en Amazon a cambio de 50 millones de dólares al año. Amazon abrió su web a otros vendedores, Toys R Us perdió años sin tienda online propia y, con la deuda de su compra en 2005, acabó quebrando en 2017.\n\nUno de los mayores errores de la historia del comercio: regalarle internet a tu rival.\n\n#negocios #marketing #amazon #toysrus #historiaempresarial",
 "sources": [
  "https://www.geekwire.com/2018/reports-longtime-retail-giant-toys-r-us-close-800-u-s-stores-30000-jobs-likely-lost/",
  "https://www.retailgazette.co.uk/blog/2018/03/toys-r-us-went-wrong-part-1/",
  "https://www.businessofbusiness.com/articles/toys-r-us-is-closing-180-us-stores-should-we-blame-amazon-or-walmart/"
 ],
 "lines": [
  {
   "say": "Toys R Us le pagaba a Amazon cincuenta millones al año, y Amazon acabó hundiéndola.",
   "show": "Toys R Us le pagaba a Amazon 50 millones al año, y Amazon acabó hundiéndola.",
   "red": [
    "50",
    "hundiéndola."
   ],
   "card": {
    "type": "money",
    "value": 50000000,
    "prefix": "$",
    "label": "Pago anual de Toys R Us a Amazon",
    "unit": "dólares al año"
   }
  },
  {
   "say": "Año dos mil, Toys R Us no quiere complicarse con internet, así que firma un trato: diez años vendiendo sus juguetes solo en Amazon.",
   "show": "Año 2000, Toys R Us no quiere complicarse con internet, así que firma un trato: 10 años vendiendo sus juguetes solo en Amazon.",
   "red": [
    "internet,",
    "Amazon."
   ],
   "card": {
    "type": "year",
    "year": 2000,
    "pills": [
     {
      "text": "10 años"
     },
     {
      "text": "Exclusiva en Amazon",
      "color": "red"
     }
    ]
   }
  },
  {
   "say": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
   "show": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
   "red": [
    "otros",
    "años"
   ],
   "card": {
    "type": "versus",
    "a_name": "Amazon",
    "a_label": "Abre a otros vendedores",
    "b_name": "Toys R Us",
    "b_label": "Sin tienda online",
    "b_ratio": 0.18
   },
   "stamp": "Demanda"
  },
  {
   "say": "Y encima, en dos mil cinco unos fondos la compran cargándola con más de cinco mil millones de deuda.",
   "show": "Y encima, en 2005 unos fondos la compran cargándola con más de 5.000 millones de deuda.",
   "red": [
    "5.000",
    "deuda."
   ],
   "card": {
    "type": "money",
    "value": 5000000000,
    "prefix": "$",
    "label": "Deuda de la compra · 2005",
    "unit": "dólares",
    "color": "white"
   }
  },
  {
   "say": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "show": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "red": [
    "cientos"
   ],
   "card": "same",
   "badge": "Cientos de millones al año"
  },
  {
   "say": "En dos mil diecisiete quiebra, y al año siguiente cierra unas ochocientas tiendas en Estados Unidos.",
   "show": "En 2017 quiebra, y al año siguiente cierra unas 800 tiendas en Estados Unidos.",
   "red": [
    "800"
   ],
   "card": {
    "type": "year",
    "year": 2017
   },
   "stamp": "Quiebra"
  },
  {
   "say": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
   "show": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
   "red": [
    "caro."
   ],
   "card": {
    "type": "text",
    "lines": [
     "Salió",
     "caro."
    ]
   }
  },
  {
   "say": "Sígueme, y cada día te cuento un caso nuevo.",
   "show": "Sígueme, y cada día te cuento un caso nuevo.",
   "red": [
    "Sígueme,"
   ],
   "card": {
    "type": "follow"
   }
  }
 ]
}
```

## 10. Ejemplo antiguo v2 con fotos (NO lo imites: manda la sección 3c)

Mismo caso Toys R Us en formato con fotos. Fíjate en: portada al principio y al final, 2–4 planos por frase, kickers cortos,
cifras gigantes en planos `number`.

```json
{
 "lines": [
  {
   "say": "Toys R Us le pagaba a Amazon cincuenta millones al año, y Amazon acabó hundiéndola.",
   "show": "Toys R Us le pagaba a Amazon 50 millones al año, y Amazon acabó hundiéndola.",
   "red": [
    "50",
    "millones",
    "hundiéndola."
   ],
   "visuals": [
    {
     "type": "title",
     "src": "img/hialeah.jpg",
     "text1": "Cómo Amazon hundió",
     "text2": "a Toys R Us"
    },
    {
     "type": "number",
     "src": "img/amz_logo.jpg",
     "value": 50000000,
     "prefix": "$",
     "label": "al año para Amazon",
     "focus": [
      0.5,
      0.4
     ]
    }
   ]
  },
  {
   "say": "Año dos mil, Toys R Us no quiere complicarse con internet, así que firma un trato: diez años vendiendo sus juguetes solo en Amazon.",
   "show": "Año 2000, Toys R Us no quiere complicarse con internet, así que firma un trato: 10 años vendiendo sus juguetes solo en Amazon.",
   "red": [
    "internet,",
    "Amazon."
   ],
   "visuals": [
    {
     "type": "img",
     "src": "img/ts_b.jpg",
     "kicker": "Año 2000",
     "focus": [
      0.5,
      0.5
     ]
    },
    {
     "type": "img",
     "src": "img/ts_c.jpg",
     "focus": [
      0.5,
      0.35
     ],
     "zoom": "out"
    },
    {
     "type": "img",
     "src": "img/fc.jpg",
     "kicker": "10 años de exclusiva",
     "focus": [
      0.4,
      0.5
     ]
    }
   ]
  },
  {
   "say": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
   "show": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
   "red": [
    "otros",
    "años"
   ],
   "visuals": [
    {
     "type": "img",
     "src": "img/bezos.jpg",
     "focus": [
      0.5,
      0.3
     ]
    },
    {
     "type": "img",
     "src": "img/amz_logo.jpg",
     "kicker": "Otros vendedores",
     "focus": [
      0.3,
      0.4
     ],
     "zoom": "out"
    },
    {
     "type": "doc",
     "src": "img/fc.jpg",
     "kicker": "Demanda",
     "lines": [
      "Toys R Us",
      "contra Amazon"
     ]
    },
    {
     "type": "img",
     "src": "img/ts_c.jpg",
     "kicker": "Años perdidos",
     "focus": [
      0.6,
      0.6
     ]
    }
   ]
  },
  {
   "say": "Y encima, en dos mil cinco unos fondos la compran cargándola con más de cinco mil millones de deuda.",
   "show": "Y encima, en 2005 unos fondos la compran cargándola con más de 5.000 millones de deuda.",
   "red": [
    "5.000",
    "deuda."
   ],
   "visuals": [
    {
     "type": "img",
     "src": "img/kingstowne.jpg",
     "kicker": "2005",
     "focus": [
      0.5,
      0.5
     ]
    },
    {
     "type": "number",
     "src": "img/kingstowne.jpg",
     "value": 5000000000,
     "prefix": "$",
     "label": "de deuda",
     "color": "red",
     "zoom": "out"
    }
   ]
  },
  {
   "say": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "show": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "red": [
    "cientos",
    "tiendas."
   ],
   "visuals": [
    {
     "type": "img",
     "src": "img/closing7.jpg",
     "kicker": "¿Y la deuda?",
     "focus": [
      0.5,
      0.5
     ]
    },
    {
     "type": "img",
     "src": "img/closing.jpg",
     "kicker": "Cientos de millones al año",
     "focus": [
      0.45,
      0.5
     ],
     "zoom": "out"
    }
   ]
  },
  {
   "say": "En dos mil diecisiete quiebra, y al año siguiente cierra unas ochocientas tiendas en Estados Unidos.",
   "show": "En 2017 quiebra, y al año siguiente cierra unas 800 tiendas en Estados Unidos.",
   "red": [
    "quiebra,",
    "800"
   ],
   "visuals": [
    {
     "type": "img",
     "src": "img/closing6.jpg",
     "kicker": "2017",
     "stamp": "Quiebra",
     "focus": [
      0.5,
      0.5
     ]
    },
    {
     "type": "number",
     "src": "img/hialeah.jpg",
     "value": 800,
     "label": "tiendas cerradas",
     "color": "red",
     "zoom": "out"
    }
   ]
  },
  {
   "say": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
   "show": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
   "red": [
    "caro."
   ],
   "visuals": [
    {
     "type": "end",
     "src": "img/closing6.jpg"
    }
   ]
  },
  {
   "say": "Sígueme, y cada día te cuento un caso nuevo.",
   "show": "Sígueme, y cada día te cuento un caso nuevo.",
   "red": [
    "Sígueme,"
   ],
   "visuals": [
    {
     "type": "title",
     "src": "img/hialeah.jpg",
     "text1": "Cómo Amazon hundió",
     "text2": "a Toys R Us"
    }
   ]
  }
 ]
}
```
