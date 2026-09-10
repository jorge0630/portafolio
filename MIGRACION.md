# Migración a template propio — Completada

Portafolio de Camilo Pacheco, reconstruido en HTML, CSS y JavaScript propios,
sin librerías ni frameworks.

- **Publicado en:** https://cp327.github.io/portafolio/
- **Local:** http://localhost/portafolio/ (XAMPP — *no* abrir con `file://`)
- **Despliegue:** GitHub Pages desde `main`, sin workflow ni paso de build
- **Estado:** los 7 pasos completados

---

## 1. Resultado

| | Antes | Ahora |
|---|---|---|
| Font Awesome | 1474 KB | — |
| Tailwind (CDN) | 400 KB | — |
| Swiper (JS + CSS) | 169 KB | — |
| CSS + JS propio | 0 | **97 KB** sin minificar |
| **Total descargado** | **~2043 KB** | **~97 KB** |

Dependencias externas que quedan: la fuente Poppins (Google Fonts) y el
endpoint de Formspree del formulario. Ninguna es necesaria para que la página
se vea correctamente.

```
Tailwind · Font Awesome · Swiper   0 referencias
onclick y <script> inline          0
<img> sin alt                      0
target="_blank" sin rel=noopener   0
data-index                         0
```

---

## 2. Restricciones del despliegue

| Restricción | Consecuencia |
|---|---|
| Pages sirve desde `main`, sin build | Todo funciona tal cual se sirve. Nada de npm ni bundlers. |
| *Project site* en subruta `/portafolio/` | **Rutas relativas siempre.** Nunca `/src/...` con barra inicial. |
| Excepción: `404.html` | Usa rutas absolutas con prefijo `/portafolio/`, porque Pages lo sirve para URLs inexistentes a cualquier profundidad. |
| Metadatos | `canonical`, Open Graph y `sitemap.xml` sí llevan la URL absoluta. |

---

## 3. Estructura

```
portafolio/
├── index.html
├── 404.html · robots.txt · sitemap.xml
├── MIGRACION.md
├── views/                       5 páginas de proyecto
└── src/
    ├── css/
    │   ├── tokens.css     Variables: la fuente única de verdad
    │   ├── reset.css      Normalización entre navegadores
    │   ├── base.css       Estilos por etiqueta + .wrapper, .skip-link
    │   └── components.css 20 componentes con nombre
    ├── js/
    │   ├── main.js               Punto de entrada (módulo ES)
    │   └── modules/
    │       ├── header.js         Sombra al hacer scroll (6 páginas)
    │       ├── nav.js            Menú móvil (solo index)
    │       ├── carousel.js       Carrusel de capturas (solo index)
    │       ├── gallery.js        Lightbox <dialog> (solo vistas)
    │       ├── contact-form.js   Envío a Formspree (solo index)
    │       └── footer-year.js    Año del pie (6 páginas)
    ├── img/icons.svg      Sprite SVG (sustituye a Font Awesome)
    └── CV - Camilo Pacheco Perez.pdf
```

**Orden de carga del CSS** — importa, no cambiarlo:

```html
<link rel="stylesheet" href="src/css/tokens.css">      <!-- define las variables -->
<link rel="stylesheet" href="src/css/reset.css">       <!-- normaliza -->
<link rel="stylesheet" href="src/css/base.css">        <!-- estilos por etiqueta -->
<link rel="stylesheet" href="src/css/components.css">  <!-- piezas con nombre -->
```

Cada módulo JS comprueba si su marcado existe, así que `main.js` es el mismo
para las 6 páginas sin condicionales.

---

## 4. Decisiones de diseño

### Tokens en dos capas

`tokens.css` separa **primitivas** (`--green-600`, `--neutral-200`) de
**semánticas** (`--color-text`, `--color-surface`). Los componentes usan solo
las semánticas. Gracias a eso el modo oscuro se define redefiniendo únicamente
esa segunda capa: **ningún componente sabe que existe un tema oscuro**.

### El verde: dos tonos

El `green-600` original daba 3.30:1 sobre blanco, por debajo del mínimo AA.

| Token | Valor | Uso | Contraste |
|---|---|---|---|
| `--color-brand` | `#16a34a` | Identidad: punto del logo, viñetas, **títulos grandes** | 3.12:1 — válido para texto grande (mínimo 3:1) |
| `--color-accent` | `#15803d` | Texto normal y botones | **5.02:1** |

> El título del hero queda en **3.12:1**, el margen más ajustado del sistema.
> Si algún día se cambia ese verde, hay que recalcularlo.

### Contraste verificado — WCAG AA en ambos temas

Calculado desde los valores de `tokens.css`, no medido en el navegador:

| Elemento | Claro | Oscuro |
|---|---|---|
| Texto principal | 13.02:1 | 16.86:1 |
| Texto secundario | 4.90:1 | 6.62:1 |
| Título de tarjeta | 5.02:1 | 9.92:1 |
| Enlace del nav | 4.90:1 | 6.62:1 |
| Texto sobre botón | 5.02:1 | 10.93:1 |
| Etiqueta de tecnología | 12.19:1 | 15.30:1 |
| Título del hero (grande) | 3.12:1 | 8.36:1 |

### `.wrapper`, no `.container`

Tailwind tenía su propia utilidad `.container` y ganaba en la cascada, lo que
provocó un bug real (el header medía 1536 px en vez de 1152 px). El nombre se
mantiene aunque Tailwind ya no esté.

### Estados en atributos, no en clases

El menú deriva su estado de `aria-expanded`; el carrusel usa `aria-current` en
los puntos; el lightbox usa `data-unica`. Así el atributo accesible y lo que se
ve **no pueden desincronizarse**.

### Por qué `<dialog>` para el lightbox

Aporta de forma nativa el atrapado del foco, el cierre con `Esc`, el fondo
(`::backdrop`), dejar inerte el resto de la página y **devolver el foco** a la
miniatura de origen. Escribir eso a mano es la parte donde más se falla.

---

## 5. Bugs corregidos

### `gallery.js` — flechas del teclado sin el visor abierto
El código anterior registraba el listener en `document` sin comprobar si el
modal estaba abierto. Pulsar `→` al cargar producía:

```js
currentIndex = (0 + 1) % 0;          // NaN
modalImg.src = currentGallery[NaN];  // undefined → petición a /views/undefined → 404
```

Ahora el listener vive en el propio `<dialog>`, que al ser modal solo recibe
eventos mientras está abierto. **Verificado:** con el visor cerrado, `src`
queda en `""` y no aparece ningún `undefined`.

### `gallery.js` — `data-index` redundante
El array se construía por orden del DOM pero el índice se leía del atributo:
coincidían por casualidad. Ahora el orden lo determina solo el DOM.
**Verificado:** 0 atributos `data-index` en el sitio.

### Swiper con `loop: true` y un solo slide
WhatsApp y B&B mostraban flechas y paginación que no hacían nada.
**Verificado:** los proyectos de una captura generan 0 controles.

### Miniaturas no accesibles por teclado
Eran `<img>` con `onclick`. Ahora son `<button>`: entran en el orden de
tabulación y el foco vuelve solo al cerrar el visor.

---

## 6. Trampas del entorno de pruebas

Tres cosas costaron tiempo por dar falsos negativos. Comprobarlas **antes** de
dar algo por roto:

| Síntoma | Causa real | Cómo detectarlo |
|---|---|---|
| Transiciones que no avanzan, scroll suave que no se mueve, `IntersectionObserver` que no entrega nada | **Pestaña en segundo plano.** No ejecuta `requestAnimationFrame`, ni scroll suave, ni observers, ni eventos `scroll` | `document.visibilityState === 'visible'` |
| Lo mismo, dentro de un `<iframe>` de pruebas | El iframe queda *throttled* (se midió 1 frame en 500 ms) | Inyectar `:root{--duration-base:0ms}` para medir estados finales |
| Estilos computados que no cuadran al cambiar `data-theme` | El recálculo no se dispara solo | Mutar el DOM (añadir y quitar un nodo) fuerza el recálculo |
| La página muestra contenido viejo tras editar el HTML | Caché del navegador | `Ctrl+Shift+R`, o añadir `?v=N` a la URL |

---

## 7. Pendiente

### A cargo de Camilo
- [ ] **Imágenes** (17 MB): mismo nombre, de `.png` a `.webp`. Al entregarlas,
      cambiar las ~25 referencias es un `sed` de un comando.
- [ ] `foto.png` (2,6 MB) e `icono2.png` (1,4 MB) **no se usan en ningún sitio**.
- [ ] `icono.png` se usa de favicon pesando **1,4 MB**; debería ser ~5 KB.
- [ ] Reactivar las URLs de los proyectos, incluida `http://72.60.127.176/`
      (sin HTTPS, Chrome la marca "No seguro").
- [ ] Verificar el carrusel y el lightbox con la ventana **en primer plano**.

### Mejoras posibles
- [ ] `README.md` y `.gitignore`.
- [ ] Botón manual de tema claro/oscuro. La arquitectura ya lo soporta: basta
      con escribir `data-theme` en `<html>` y guardarlo en `localStorage`.
- [ ] Scroll-spy para marcar la sección activa en el nav. El CSS ya contempla
      `.site-nav__link[aria-current='true']`.
- [ ] Textos `alt` más descriptivos en las capturas (ahora son "captura N de M").
- [ ] Autoalojar Poppins para eliminar la última dependencia externa de diseño.

---

## 8. Cómo verificar

```bash
# ¿Queda alguna librería?
grep -rio 'tailwind\|font-awesome\|swiper' --include=*.html .   # debe dar 0

# ¿Recursos rotos?
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/portafolio/
```

En el navegador, con la ventana **en primer plano**:

```js
document.visibilityState                      // "visible" — si no, nada de lo de abajo es fiable
document.querySelectorAll('h1').length        // 1 en cada página
document.querySelectorAll('a[href="#"]').length // 0

// Desplazamiento de layout acumulado (objetivo < 0.1)
new PerformanceObserver(l => l.getEntries().forEach(e => console.log(e.value)))
  .observe({ type: 'layout-shift', buffered: true });
```
