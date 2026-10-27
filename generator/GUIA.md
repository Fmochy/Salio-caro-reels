# Salió caro — guía del reel diario

Cuenta de Instagram **@salio.caro** ("Salió caro | Errores de marcas"): cada día un reel de ~30–40 s
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

Duración: los más vistos del nicho duran 30–60 s; apunta a **30–40 s**. Si el guion pasa de 105 palabras, recorta.
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
- **8–11 frases, 85–110 palabras en total** (≈30–40 s). Frases cortas, castellano de España, tono directo de contar una historia.
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

Ejemplo completo (Toys R Us, el modelo a imitar):

```json
{
 "formato": "hibrido",
 "slug": "toysrus-amazon",
 "lines": [
  {
   "say": "Toys R Us le pagaba a Amazon cincuenta millones al año, y Amazon acabó hundiéndola.",
   "show": "Toys R Us le pagaba a Amazon 50 millones al año, y Amazon acabó hundiéndola.",
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
     "at": 0.3
    },
    {
     "type": "texto",
     "text": "50 M$ al año",
     "color": "green",
     "highlight": true,
     "at": 0.35
    },
    {
     "type": "texto",
     "text": "...y la hundió",
     "font": "mano",
     "color": "red",
     "underline": true,
     "at": 0.7
    }
   ]
  },
  {
   "say": "Año dos mil, Toys R Us no quiere complicarse con internet, así que firma un trato: diez años vendiendo sus juguetes solo en Amazon.",
   "show": "Año 2000, Toys R Us no quiere complicarse con internet, así que firma un trato: 10 años vendiendo sus juguetes solo en Amazon.",
   "layout": "foto_lado",
   "photos": [
    {
     "src": "img/ts_b.jpg"
    }
   ],
   "notes": [
    {
     "type": "rodear",
     "text": "2000",
     "at": 0.05
    },
    {
     "type": "contrato",
     "text": "10 años, solo Amazon",
     "at": 0.45
    }
   ]
  },
  {
   "say": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
   "show": "Pero ojo, Amazon empieza a dejar que otros vendan juguetes en su web. Toys R Us la denuncia y gana, pero ya había perdido años sin tienda online propia.",
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
     "at": 0.1
    },
    {
     "type": "check",
     "text": "Denuncia: gana",
     "at": 0.45
    },
    {
     "type": "web",
     "text": "toysrus.com",
     "at": 0.65
    }
   ]
  },
  {
   "say": "Y encima, en dos mil cinco unos fondos la compran cargándola con más de cinco mil millones de deuda.",
   "show": "Y encima, en 2005 unos fondos la compran cargándola con más de 5.000 millones de deuda.",
   "layout": "uno",
   "photos": [
    {
     "src": "img/kingstowne.jpg"
    }
   ],
   "notes": [
    {
     "type": "texto",
     "text": "2005: la compran unos fondos",
     "font": "mano",
     "at": 0.15
    },
    {
     "type": "bola",
     "text": "5.000 M$",
     "label": "DEUDA",
     "at": 0.55
    }
   ]
  },
  {
   "say": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "show": "¿Sabes qué hacía esa deuda? Se comía cientos de millones cada año, dinero que no llegaba a las tiendas.",
   "layout": "uno",
   "photos": [
    {
     "src": "img/closing7.jpg"
    }
   ],
   "notes": [
    {
     "type": "monedas",
     "text": "DEUDA",
     "at": 0.3
    },
    {
     "type": "texto",
     "text": "cientos de millones al año",
     "font": "mano",
     "color": "red",
     "at": 0.6
    }
   ]
  },
  {
   "say": "En dos mil diecisiete quiebra, y al año siguiente cierra unas ochocientas tiendas en Estados Unidos.",
   "show": "En 2017 quiebra, y al año siguiente cierra unas 800 tiendas en Estados Unidos.",
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
     "label": "tiendas cerradas en EE. UU.",
     "at": 0.5
    }
   ]
  },
  {
   "say": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
   "show": "A Toys R Us, regalarle internet a Amazon le salió muy caro.",
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
     "at": 0.55
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
Duración ideal 28–42 s; si pasa de 45 s, recorta frases.

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

## 9. Ejemplo de referencia (modelo a imitar)

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

## 10. Ejemplo v2 con fotos (modelo de `visuals`)

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
