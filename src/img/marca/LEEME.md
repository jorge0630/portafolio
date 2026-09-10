# Marca

Monograma **JQ entre etiquetas de código**, en DM Serif Display Italic.

Todo se genera con `generar.py`. No hay ningún archivo de diseño que editar a
mano: las piezas salen de las tipografías, y los números que las componen
están en ese script.

```
python generar.py
```

## Qué es cada archivo

| Archivo | Qué contiene | Dónde se usa |
|---|---|---|
| `marca.svg` | Monograma `< (JQ) />` | Copia suelta, por si hace falta fuera del sitio |
| `firma.svg` | Marca + separador + «Jorge Quejada / Software Developer» | Copia suelta |
| `favicon.png` | Solo círculo y monograma, 64×64 | Favicon de las 9 páginas |
| `generar.py` | Genera todo lo anterior | — |
| `_fuentes/` | Tipografías descargadas | Solo para generar; no se sirve |

> **En el sitio no se usan los `.svg` de esta carpeta.** El navbar y el pie
> tiran de `../icons.svg`, donde `generar.py` inyecta los símbolos `#i-marca`
> e `#i-firma`. Los archivos sueltos existen para usos externos: una tarjeta,
> una firma de correo, un perfil.

## Las dos decisiones que sostienen esto

### 1. El texto va vectorizado

Las letras no son `<text>`, son curvas. Un logotipo no puede depender de que
una webfont llegue a cargar: si la red falla, se vería con la tipografía de
reserva, que no es la marca.

Tiene un efecto secundario que conviene no perder: **DM Serif Display no se
carga en el sitio**. Existe solo dentro de estos contornos, así que el
monograma no añade ninguna petición ni ningún kilobyte de fuente. El `</>` y
el rol usan Archivo, que el sitio ya carga de todos modos.

### 2. Una sola pieza, no tres variantes de color

Se sirve como `<use href="icons.svg#i-marca">`, no como `<img>`. Así el dibujo
hereda `color` del CSS: índigo en el navbar, casi blanco sobre la franja del
pie, y lo que haga falta en cualquier otro sitio.

El esquema anterior de este portafolio era PNG, y por eso necesitaba tres
variantes de color —verde, blanca y negra— de cada pieza, más regenerarlas
enteras cada vez que cambiara la paleta. Aquí la paleta puede cambiar sin
tocar un solo archivo de marca.

## El color del favicon

`#5264ff`. **No es un token de la rampa.** Un favicon se ve sobre la barra del
navegador, que puede ser clara u oscura, así que no puede optimizarse para una
sola. Ese valor sale de barrer la luminosidad en el matiz 272 buscando el
punto donde el contraste del *peor* de los dos temas es máximo: **4,24:1 tanto
en claro como en oscuro**. Ningún tono de la rampa lo iguala — `indigo-500` da
3,66:1 y `indigo-600` 3,46:1.

## El favicon lleva menos dibujo

A 16 px el `</>` es una mancha, así que el favicon lleva **solo el círculo y el
monograma**. Es la práctica normal: la marca completa para tamaños grandes y
una versión reducida a lo esencial para el icono.

## Si hay que retocar el dibujo

Los números vivos están en la función `construir()` de `generar.py`:

| Qué | Dónde |
|---|---|
| Tamaño de las letras dentro del círculo | `alto=44` (marca) y `alto=40` (firma) |
| Separación entre la J y la Q | `tracking=40` |
| Radio y grosor del círculo | `r="44"`, `stroke-width="3.5"` |
| Posición de `<` y `/>` | `cx=24` y `cx=184` |
| Tracking de «SOFTWARE DEVELOPER» | `tracking=95` |

`generar.py` se puede ejecutar las veces que haga falta: limpia los símbolos
anteriores del sprite antes de escribir los nuevos, y comprueba que no quede
duplicado ninguno.

## Tipografías

Las dos con licencia **SIL Open Font License**, de uso libre incluso comercial.
`generar.py` las descarga a `_fuentes/` la primera vez.

| Tipografía | Para qué |
|---|---|
| [DM Serif Display Italic](https://fonts.google.com/specimen/DM+Serif+Display) | Monograma JQ y el nombre |
| [Archivo](https://fonts.google.com/specimen/Archivo) | `</>` y «SOFTWARE DEVELOPER» |

Se eligió DM Serif Display tras comparar seis opciones al tamaño real del
navbar (31 px). Playfair Display, más parecida a la firma original, es un
serif de contraste alto: sus trazos finos caen por debajo de un píxel al
reducir y el monograma se emborrona. DM Serif tiene el trazo grueso y parejo,
así que conserva la elegancia sin partes que se pierdan.

## Lo que falta

- **Las piezas del portafolio anterior siguen en la carpeta**
  (`marca-verde.png`, `firma-blanca.png`, `marca-negra.png` y compañía). Ya no
  las referencia ninguna página; se pueden borrar, junto con
  `../originales/`, que solo servía para regenerarlas.
- **No hay versión sobre fondo de color pleno.** Si algún día hace falta el
  logotipo dentro de un cuadro índigo —una foto de perfil, un avatar—, se
  añade un `<symbol>` más con el círculo relleno en vez de contorneado.
