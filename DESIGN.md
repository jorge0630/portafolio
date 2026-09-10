# Design

Sistema visual del portafolio. La estrategia y el porqué están en
[PRODUCT.md](PRODUCT.md); aquí está el cómo.

Implementado en `src/css/tokens.css` (variables) y `src/css/components.css`
(piezas). Este documento describe lo que existe, no una aspiración.

---

## Dirección

**Editorial estructural, no editorial de revista.**

La dirección elegida fue "editorial tipográfico", pero la referencia de marca
señala ese carril como saturado, con una huella concreta: serif display en
cursiva, etiquetas mono en versalitas, columnas separadas por reglas,
monocromía y cero imágenes.

Se conserva lo que aportaba (jerarquía fuerte, aire, datos a la vista,
composición asimétrica) y se descarta la piel que lo delata:

| Se descarta | Se hace en su lugar |
|---|---|
| Serif display en cursiva | Una grotesca de señalética, en negro y estrecha |
| Etiquetas en versalitas sobre cada sección | Ninguna. La numeración solo aparece en proyectos, donde identifica una pieza |
| Monocromía contenida | Índigo comprometido: superficies enteras, con ámbar de contrapunto |
| Sin imágenes | Las capturas reales son la columna vertebral |

El ángulo diferencial es el contenido, no el gesto: sistemas industriales en
Cartagena, no software de startup.

---

## Color

Definido en **OKLCH**. Ningún neutro es blanco ni negro puro: todos llevan
croma 0.002–0.015 en el matiz de marca (272), lo que integra los grises con
el índigo en lugar de dejarlos sueltos.

### Estrategia: comprometida, a dos colores

**Índigo** es la marca y hace el trabajo estructural. No es un acento del 10%:
**carga superficies enteras** en la franja posterior al hero, en el pie y en
las cabeceras de las vistas de proyecto. Entre esos momentos el fondo es
neutro, y el contraste entre ambos es lo que hace que el color se recuerde.

**Ámbar** es el contrapunto, y su valor depende de que sea escaso. Aparece en
tres sitios y en ninguno más:

| Dónde | Token | Por qué ahí |
|---|---|---|
| El bloque tras el retrato del hero | `--color-highlight` | Es la mancha de color más grande de la mitad superior. En índigo se fundiría con el titular y los botones, y el hero quedaría monocromo |
| Los números de proyecto (`01`, `02`…) | `--color-highlight-strong` | Es la única lista numerada de la página; el color secundario la separa sin subir tamaño ni peso |
| Las etiquetas dentro de la franja | `--color-on-brand-accent` | Rompe por dentro el rectángulo de color más grande del sitio |

> La regla es la proporción. Si el ámbar se reparte por toda la página, los
> dos colores compiten y no manda ninguno. Ante la duda: índigo.

### Anclaje

La rampa índigo está anclada al `600`, que resuelve a `#4655ec`: croma alta
para no leerse como «azul de sistema operativo», con la deriva justa hacia el
violeta que lo separa del azul corporativo genérico.

En la rampa ámbar **el matiz gira al bajar** (86° arriba, 52° abajo) en lugar
de mantenerse fijo. Un amarillo puro oscurecido a matiz constante se vuelve
verde oliva; girándolo hacia el naranja, los tonos oscuros siguen leyéndose
como ámbar.

### Los cuatro tonos que importan

| Token | Valor (tema claro) | Para qué | Regla |
|---|---|---|---|
| `--color-brand` | `oklch(0.535 0.225 272)` | Identidad: punto del logo, énfasis del titular, viñetas | **Solo texto grande** (5.22:1, pero es el rol) |
| `--color-accent` | `oklch(0.462 0.205 272)` | Todo el texto normal, botones, enlaces | 7.13:1 |
| `--color-brand-surface` | `oklch(0.392 0.170 273)` | Franjas de color pleno | Con `--color-on-brand` encima |
| `--color-highlight` | `oklch(0.655 0.150 60)` | Ámbar en elementos gráficos y texto grande | **3.11:1 — no vale para texto pequeño** |

> El error más fácil de cometer aquí es usar `--color-highlight` en texto
> pequeño: se queda en 3.11:1, por debajo del mínimo AA. Para texto de menos
> de 24px en ámbar existe `--color-highlight-strong` (6.64:1). En tema oscuro
> los dos apuntan al mismo tono, porque ahí el ámbar vivo ya da 9.84:1.

### Texto terciario: dos primitivas

`--neutral-450` y `--neutral-550` existen porque **ningún valor único cumple
AA en los dos temas**: sobre fondo claro hace falta L ≤ 0.53 y sobre fondo
oscuro L ≥ 0.61. Cada tema mapea el suyo en `--color-text-subtle`.

### Verde: solo para el estado de éxito

`--emerald-400/700` no forma parte de la identidad. Existe porque el verde es
la convención de «ha ido bien» en el mensaje del formulario, y ni el índigo ni
el ámbar comunican eso sin ambigüedad.

### Contraste verificado

43 pares comprobados en tema claro y oscuro, calculados desde los valores de
`tokens.css` con conversión OKLCH → sRGB. **Todos los que se dan en la página
cumplen WCAG AA.** Toda la rampa cae además dentro del gamut sRGB, así que el
navegador pinta el color calculado sin recortarlo.

Una única combinación teórica se queda en 4.37:1 —`--color-text-subtle` sobre
`--color-surface-hover` en tema oscuro—, pero **no se da**: `--color-surface-hover`
no lo usa ningún componente. Si algún día se usa, ese par hay que recalcularlo.

---

### La marca

El logotipo es una pieza raster con textura desgastada, no un vector. Vive en
`src/img/marca/` con su propio LEEME; aquí solo lo que afecta al sistema visual.

Se usa en dos sitios y con dos recortes distintos:

- **Navbar**: solo la marca (corona + monograma). Alta a 1.75em porque es casi
  cuadrada y la corona ocupa el tercio superior: por debajo de esa altura sus
  trazos finos se empastan.
- **Pie**: la firma completa —marca, separador y nombre + rol— en casi blanco.
  Un pie es una despedida, y ahí una firma cierra en vez de decorar. Va al 85%
  de opacidad para no competir con «Hablemos.».

> ⚠️ **Pendiente: el logotipo sigue siendo el anterior.** Los archivos de
> `src/img/marca/` son el monograma del autor original y están recoloreados al
> verde `#008A39` de la paleta vieja, así que hoy desentonan contra el índigo.
> Se reemplazan por completo al poner la marca propia.

**El tono de marca no sirve sobre la franja de marca**: cualquier índigo
legible sobre fondo neutro se hunde contra la franja índigo del pie. De ahí
que hagan falta variantes de color y no una sola.

Cuando se genere el logotipo nuevo, el tono para la variante de color es
**`#5264ff`** = `oklch(0.582 0.228 272)`. No es un token de la rampa: sale de
barrer la luminosidad en el matiz 272 buscando el punto donde el contraste del
*peor* de los dos temas es máximo — **4.24:1 en claro y oscuro**. Ningún tono
de la rampa lo iguala (`indigo-500` da 3.66:1 y `indigo-600` 3.46:1). Para la
variante clara del pie, `--color-on-brand` = `#f0f3fe`, que da 9.14:1 sobre la
franja en claro y 12.30:1 en oscuro.

## Tipografía

**Archivo**, una sola familia, variable en peso (400–800) y anchura (75–125).

Se eligió por lo que representa como objeto físico: una placa de equipo
industrial o un rótulo de señalética, no una landing de producto. Encaja con
la historia portuaria y operativa del contenido.

Una familia con contraste fuerte de peso y ancho es más sólida que un par
display + cuerpo elegido por costumbre.

| Uso | Tamaño | Peso | Anchura |
|---|---|---|---|
| Titular del hero | `--text-display` (hasta 8.5rem) | 800 | 88% |
| Títulos de sección | `--text-3xl` | 700 | 94% |
| Cita de la franja | `--text-4xl` | 700 | 92% |
| Cuerpo | `--text-base` | 400 | 100% |
| Etiquetas | `--text-xs` en mayúsculas | 600 | 100% |

Escala modular ~1.28 con `clamp()`. Los saltos son grandes a propósito: una
escala plana se lee como falta de decisión.

En tema oscuro, `--leading-normal` y `--leading-relaxed` suben 0.05 y 0.07:
el texto claro sobre fondo oscuro se percibe más fino y pide más aire.

---

## Layout

- Ancho máximo **78rem**, canalón fluido `clamp(1.25rem, 5vw, 3rem)`.
- Separación entre secciones `clamp(5rem, 11vw, 10rem)`. Generosa a propósito.
- **Hero asimétrico**: 1.45fr para el texto, 0.55fr para el retrato, que además
  baja 4rem respecto a la línea superior para romper el eje.
- **El aire sobre el hero es corto**: `clamp(1.5rem, 2.5vw, 2.5rem)`, unos 38px
  en escritorio. La separación generosa del sistema es la de *entre* secciones;
  el header es una barra fina, no una sección, y aplicarle la misma escala
  dejaba 96px hasta la línea de datos y 150px hasta el titular — una banda vacía
  que no separaba nada y empujaba los botones fuera de la primera pantalla.
  El suelo de 1.5rem no es arbitrario: por debajo de ~24px la línea de datos
  roza el header, que en reposo no tiene borde.
- **Proyectos en filas alternas**, no en rejilla de tarjetas. Las filas pares
  invierten el orden de la imagen.
- **Franjas a sangre completa por estructura**, nunca con
  `margin-inline: calc(50% - 50vw)`: ese truco desborda exactamente el ancho de
  la barra de scroll y provoca desplazamiento horizontal.

### Móvil

Tres decisiones propias, todas medidas a 375px y comprobadas a 305px:

- **El panel del menú va a `left/right: 0`, no a `-gutter`.** Su contexto de
  posicionamiento es `.site-header__inner`, que *es* el `.wrapper`: su gutter es
  `padding-inline`, así que su caja ya llega de borde a borde. Sacarlo otro
  gutter lo hacía 40px más ancho que la pantalla, y eso producía **dos fallos a
  la vez**: la página se arrastraba en horizontal y el texto de los enlaces caía
  justo sobre el borde izquierdo, como si estuviera cortado.
- **La ficha de datos apila la etiqueta sobre el valor.** A dos columnas la
  etiqueta se comía 5.5rem de los ~21rem disponibles y los valores largos caían
  en tres líneas quebradas. Las dos columnas vuelven a partir de 48em.
- **Una regla separa un proyecto del siguiente.** En una sola columna la
  separación no basta: la captura del proyecto siguiente parece pertenecer al
  bloque anterior. Desaparece a partir de 62em, donde las filas alternan lado y
  el cambio de eje ya marca el corte.

En las vistas de proyecto, «Volver al portafolio» se recorta a «Volver» por
debajo de 30em: con la marca completa al lado, el texto entero partía el header
en dos líneas.

### Dos niveles de proyecto

Con ocho proyectos, ocho filas a sangre completa convierten la portada en un
scroll sin final y le quitan peso justo a los dos que deben dominar. Los cuatro
destacados conservan la fila alterna; los otros cuatro bajan a `.brief`.

`.brief` es **una lista separada por reglas, no una rejilla de tarjetas**. La
tarjeta era el reflejo evidente y habría sido un error doble: es la
anti-referencia principal de [PRODUCT.md](PRODUCT.md), y además cuatro tarjetas
idénticas les devuelven exactamente el peso visual que se les quería quitar.

| Pieza | Decisión |
|---|---|
| Miniatura | 16/10 y pequeña a propósito: `12rem` desde 48em, `15rem` desde 62em |
| Descripción | `max-width: 58ch` |
| Pie (enlace + stack) | **El mismo `58ch`**. Sin ese tope, en pantallas anchas el stack se va al borde derecho del contenedor mientras el texto termina mucho antes, y los dos dejan de leerse como parte de la misma ficha |
| Por debajo de 48em | Una sola columna, sin `grid-template-columns`. No hay ningún ancho fijo en toda la pieza |

---

## Movimiento

Curvas exponenciales de salida (`--ease-out-quint` por defecto). Sin rebote ni
elástico. Solo se animan `opacity` y `transform`.

| Pieza | Comportamiento |
|---|---|
| Revelado al scroll | Opacidad y 1.75rem de desplazamiento, `IntersectionObserver`, una sola vez |
| Grupos escalonados | 90ms de retardo por hijo, índice escrito desde JS |
| Retrato del hero | El bloque verde se desplaza al pasar el ratón |
| Capturas | Escala 1.025 al pasar el ratón, 900ms |
| Punto de disponibilidad | Latido de 2.6s, se detiene con movimiento reducido |

**Dos reglas que no se negocian:**

1. El contenido **nunca** se oculta si el JavaScript no corre. El estado
   oculto depende de `[data-js]`, que solo escribe `reveal.js`.
2. Hay un **seguro de 3 segundos**: si el observador no llega a entregar nada
   (pestaña en segundo plano al cargar, extensión que interfiere), se revela
   todo. Perder la animación es aceptable; perder el contenido no.

`prefers-reduced-motion` pone las cuatro duraciones a 0.01ms, lo que desactiva
todo el movimiento del sitio de golpe.

---

## Vistas de proyecto

Misma dirección que la portada, con tres decisiones propias:

- **La ficha de datos vive en la cabecera verde.** Rol, periodo, estado y stack
  se ven sin bajar. Es lo que convierte la página en un caso de trabajo y no en
  un artículo de blog.
- **La franja verde lleva el aire repartido de forma asimétrica**: 48px arriba y
  80px abajo en escritorio. Simétrica a 96px repetía el problema del hero de la
  portada — el título del proyecto aparecía a 96px del header sin nada en medio.
  Un titular de portada se apoya en el borde superior; el aire que necesita va
  debajo, separándolo de la ficha.
- **El primer titular de la página tiene su propia separación de la franja.**
  El ritmo entre secciones lo pone `.page > * + *`, y `* + *` solo separa
  *entre* hermanos: el primer hijo se quedaba sin nada y «Las capturas» tocaba
  el borde verde a 0px. Lo resuelve `.page-hero + .page`. No usa
  `--space-section` (160px) sino `clamp(4rem, 7vw, 6rem)`: se sale de una franja
  de color, y el salto de color ya hace parte del trabajo de separar.
- **Las capturas van primero**, justo después de la cabecera, y la primera
  ocupa el ancho completo. Son la única prueba de que el sistema existe;
  enterrarlas al final desaprovecha el activo más fuerte.
- **Secciones reescritas en lenguaje de caso**: "El problema", "Qué construí",
  "Retos técnicos", "Qué me llevo". Antes eran "Descripción general",
  "Objetivos principales", "Aprendizajes", que es el índice de una plantilla.
- **Navegación entre proyectos** al final. Sin ella, la única salida es el
  botón de volver y se pierde a quien acaba de leer un caso entero.

---

## Sobre los textos alternativos

El visor usa el `alt` de cada captura **como pie de foto** (`gallery.js` lo
copia en el `figcaption`). Un `alt` genérico tipo «captura 3 de 6» no es solo
una carencia de accesibilidad: sale escrito en pantalla debajo de la imagen.

Las páginas nuevas —AG Identity, ArgosMonitors y Southern Roofing— ya describen
lo que se ve en cada captura. Las cinco anteriores siguen con el texto
numerado.

---

## Pendiente

- `alt` descriptivos en las capturas de **SITI Colombia, AgroIA, WhatsApp, B&B y
  GoodMovies**, que aún usan «— captura N de M» y por tanto lo muestran como pie
  en el visor.
- Botón manual de tema. La arquitectura ya lo soporta: basta escribir
  `data-theme` en `<html>` y guardarlo en `localStorage`.
- Scroll-spy en el nav; el CSS ya contempla `.site-nav__link[aria-current]`.
- Las capturas nuevas son **JPEG de ~1536×674**, más anchas que la proporción
  `1920/1020` de `.project__img`, así que se recortan por abajo. Se ve bien
  porque el recorte respeta `object-position: top center`, pero convertirlas a
  WebP y a la proporción correcta ahorraría peso y evitaría el recorte.
