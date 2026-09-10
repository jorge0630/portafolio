# -*- coding: utf-8 -*-
"""
Genera todas las piezas de marca de Jorge Quejada.

    python generar.py

Produce:
    marca.svg      monograma JQ entre etiquetas de código
    firma.svg      marca + separador + nombre + rol
    favicon.png    64x64, versión reducida a lo esencial
    ../icons.svg   inyecta/actualiza los <symbol> i-marca e i-firma

POR QUÉ EL TEXTO VA VECTORIZADO
    Un logotipo no puede depender de que una webfont llegue a cargar: si la
    red falla, se vería con la tipografía de reserva, que no es la marca. Aquí
    las letras se convierten en curvas, así que el archivo no necesita ninguna
    fuente instalada ni descargada.

    Efecto secundario útil: DM Serif Display NO se carga en el sitio. Existe
    solo dentro de estos contornos, así que no añade ninguna petición.

POR QUÉ VIVE EN EL SPRITE
    Al servirse como <use href="icons.svg#i-marca"> el dibujo hereda `color`,
    de modo que UNA definición sirve para el navbar índigo, para el pie casi
    blanco y para cualquier fondo. El esquema anterior era PNG, y por eso
    necesitaba tres variantes de color que había que regenerar cada vez que
    cambiaba la paleta.

REQUISITOS
    pip install fonttools pillow
    Las tipografías se descargan solas la primera vez a _fuentes/ (hace falta
    red). Ambas son SIL Open Font License, de uso libre.
"""

import os
import re
import urllib.request

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.misc.transform import Transform
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.join(AQUI, "_fuentes")
SPRITE = os.path.join(AQUI, "..", "icons.svg")

DESCARGAS = {
    "dmserif.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/dmserifdisplay/DMSerifDisplay-Italic.ttf",
    "archivo.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf",
}

# El tono del favicon. No es un token de la rampa: sale de barrer la
# luminosidad en el matiz 272 buscando el punto donde el contraste del PEOR de
# los dos temas es máximo (4.24:1 en claro y oscuro). Un favicon se ve sobre
# la barra del navegador, que puede ser clara u oscura.
COLOR_FAVICON = (0x52, 0x64, 0xFF, 255)


# ---------------------------------------------------------------- tipografía
def asegurar_fuentes():
    os.makedirs(FUENTES, exist_ok=True)
    for nombre, url in DESCARGAS.items():
        destino = os.path.join(FUENTES, nombre)
        if not os.path.exists(destino):
            print(f"  descargando {nombre}...")
            urllib.request.urlretrieve(url, destino)
    return {n: os.path.join(FUENTES, n) for n in DESCARGAS}


def cargar(ruta, **ejes):
    """Carga una fuente; si es variable, la congela en los ejes pedidos."""
    f = TTFont(ruta)
    if ejes and "fvar" in f:
        f = instancer.instantiateVariableFont(f, ejes)
    return f


def medir(f, texto, tracking=0):
    """Caja real de los trazos (no la métrica, que lleva espacios laterales)."""
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    nombres = [cmap[ord(c)] for c in texto]
    anchos = [hmtx[n][0] for n in nombres]

    caja, x = None, 0
    for n, w in zip(nombres, anchos):
        bp = BoundsPen(gs)
        gs[n].draw(bp)
        if bp.bounds:
            x0, y0, x1, y1 = bp.bounds
            c = (x0 + x, y0, x1 + x, y1)
            caja = c if caja is None else (
                min(caja[0], c[0]), min(caja[1], c[1]),
                max(caja[2], c[2]), max(caja[3], c[3]))
        x += w + tracking
    return caja, nombres, anchos


def a_path(f, texto, alto=None, tam=None, tracking=0,
           cx=None, cy=None, x=None, y=None):
    """Path SVG del texto posicionado, y su caja ya en el lienzo.

    alto/tam  cómo escalar · cx,cy centrar la caja real · x,y alinear
    Devuelve (d, (x0, y0, x1, y1)).
    """
    gs = f.getGlyphSet()
    upem = f["head"].unitsPerEm
    caja, nombres, anchos = medir(f, texto, tracking)
    x0, y0, x1, y1 = caja
    ancho_real, alto_real = x1 - x0, y1 - y0

    escala = (alto / alto_real) if alto else (tam / upem)
    tx = (cx - (x0 + ancho_real / 2) * escala) if cx is not None else (x - x0 * escala)
    ty = (cy + (y0 + alto_real / 2) * escala) if cy is not None else y

    partes, avance = [], 0
    for n, w in zip(nombres, anchos):
        pen = SVGPathPen(gs, ntos=lambda v: f"{v:.2f}")
        gs[n].draw(TransformPen(
            pen, Transform(escala, 0, 0, -escala, tx + avance * escala, ty)))
        d = pen.getCommands()
        if d:
            partes.append(d)
        avance += w + tracking

    # Caja en coordenadas del lienzo: el eje Y va invertido respecto a la
    # fuente, así que la altura se mide hacia arriba desde la línea base.
    cx_final = tx + x0 * escala + ancho_real * escala / 2
    cy_final = ty - y0 * escala - alto_real * escala / 2
    an, al = ancho_real * escala, alto_real * escala
    return " ".join(partes), (cx_final - an / 2, cy_final - al / 2,
                              cx_final + an / 2, cy_final + al / 2)


def envolver(cajas, margen=1.0):
    """viewBox que ciñe las cajas, SIEMPRE con origen en 0 0.

    Devuelve (viewBox, dx, dy): el desplazamiento que hay que aplicarle al
    dibujo para llevarlo a ese origen.

    El origen 0 0 no es cosmético, es obligatorio. Al pintar un <symbol> con
    <use>, el navegador sitúa el contenido en el 0,0 del sistema de
    coordenadas; si el viewBox arranca en otro punto, el dibujo se desplaza
    hacia arriba y a la izquierda y esa franja queda fuera de la ventana. Con
    el viewBox "4.7 30.25 ..." de la firma se perdían 30 de las 97 unidades de
    alto: casi un tercio, cortado por arriba.

    Se ciñe igual que antes —un viewBox más grande que el dibujo es aire
    muerto que el navegador reserva sin pintar— pero el resultado se traslada
    al origen en lugar de dejarlo donde cayó.
    """
    x0 = min(c[0] for c in cajas) - margen
    y0 = min(c[1] for c in cajas) - margen
    x1 = max(c[2] for c in cajas) + margen
    y1 = max(c[3] for c in cajas) + margen
    fmt = lambda v: f"{v:.6g}"
    return f"0 0 {fmt(x1 - x0)} {fmt(y1 - y0)}", -x0, -y0


def trasladar(cuerpo, dx, dy):
    """Envuelve el dibujo en un <g> que lo lleva al origen del viewBox."""
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return cuerpo
    nl = chr(10)
    sangrado = nl.join(("  " + l) if l.strip() else l
                       for l in cuerpo.split(nl))
    return (f'  <g transform="translate({dx:.6g}, {dy:.6g})">' + nl
            + sangrado + nl + '  </g>')


# ------------------------------------------------------------------ dibujos
def construir(rutas):
    serif = cargar(rutas["dmserif.ttf"])
    sans600 = cargar(rutas["archivo.ttf"], wght=600, wdth=100)
    sans700 = cargar(rutas["archivo.ttf"], wght=700, wdth=100)

    # --- Marca ·  <  (JQ)  />
    R, GROSOR = 44, 3.5
    caja_circulo = (105 - R - GROSOR / 2, 60 - R - GROSOR / 2,
                    105 + R + GROSOR / 2, 60 + R + GROSOR / 2)

    jq, c_jq = a_path(serif, "JQ", alto=44, tracking=40, cx=105, cy=60)
    men, c_men = a_path(sans600, "<", alto=34, cx=24, cy=60)
    may, c_may = a_path(sans600, "/>", alto=34, cx=184, cy=60)

    marca = f'''  <circle cx="105" cy="60" r="{R}" fill="none" stroke="currentColor" stroke-width="{GROSOR}"/>
  <path d="{jq}"/>
  <path d="{men}" opacity="0.55"/>
  <path d="{may}" opacity="0.55"/>'''
    vb_marca, dx, dy = envolver([caja_circulo, c_jq, c_men, c_may])
    marca = trasladar(marca, dx, dy)

    # --- Firma · marca + separador + nombre + rol
    Rf, Gf = 42, 3.5
    caja_circ_f = (92 - Rf - Gf / 2, 75 - Rf - Gf / 2, 92 + Rf + Gf / 2, 75 + Rf + Gf / 2)

    f_jq, c1 = a_path(serif, "JQ", alto=40, tracking=40, cx=92, cy=75)
    f_men, c2 = a_path(sans600, "<", alto=31, cx=20, cy=75)
    f_may, c3 = a_path(sans600, "/>", alto=31, cx=166, cy=75)
    nombre, c4 = a_path(serif, "Jorge Quejada", tam=52, x=246, y=76)
    rol, c5 = a_path(sans700, "SOFTWARE DEVELOPER", tam=21, tracking=95, x=250, y=110)

    firma = f'''  <circle cx="92" cy="75" r="{Rf}" fill="none" stroke="currentColor" stroke-width="{Gf}"/>
  <path d="{f_jq}"/>
  <path d="{f_men}" opacity="0.55"/>
  <path d="{f_may}" opacity="0.55"/>

  <line x1="210" y1="32" x2="210" y2="118" stroke="currentColor" stroke-width="2" opacity="0.35"/>

  <path d="{nombre}"/>
  <path d="{rol}"/>
  <line x1="250" y1="124" x2="362" y2="124" stroke="currentColor" stroke-width="4.5" opacity="0.6" stroke-linecap="round"/>'''
    # Las cajas de las líneas incluyen el grosor del trazo, que se pinta
    # a ambos lados del eje; el subrayado además lleva stroke-linecap="round",
    # que lo alarga medio grosor por cada extremo.
    vb_firma, dxf, dyf = envolver([caja_circ_f, c1, c2, c3, c4, c5,
                                   (209, 32, 211, 118),
                                   (250 - 2.25, 124 - 2.25, 362 + 2.25, 124 + 2.25)])
    firma = trasladar(firma, dxf, dyf)

    # Un <symbol> pintado con <use> DEBE tener el viewBox en el origen: si
    # arranca en otro punto, el navegador desplaza el dibujo y recorta esa
    # franja. Aquí se comprueba porque el síntoma es sutil —el logotipo solo
    # se ve "un poco cortado"— y es fácil no atribuirlo a esto.
    for etiqueta, vb in (("marca", vb_marca), ("firma", vb_firma)):
        assert vb.startswith("0 0 "), (
            f"el viewBox de la {etiqueta} no empieza en el origen: {vb!r}")

    print(f"  viewBox marca: {vb_marca}")
    print(f"  viewBox firma: {vb_firma}")
    return (marca, vb_marca), (firma, vb_firma)


def escribir_svgs(marca, firma):
    (d_marca, vb_marca), (d_firma, vb_firma) = marca, firma
    cabecera = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                "<!-- Generado por generar.py. Texto vectorizado; color por currentColor. -->\n")
    piezas = {
        "marca.svg": (cabecera + f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_marca}"'
                      ' fill="currentColor" role="img" aria-label="JQ">\n' + d_marca + "\n</svg>\n"),
        "firma.svg": (cabecera + f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb_firma}"'
                      ' fill="currentColor" role="img"'
                      ' aria-label="Jorge Quejada, Software Developer">\n' + d_firma + "\n</svg>\n"),
    }
    for nombre, contenido in piezas.items():
        with open(os.path.join(AQUI, nombre), "w", encoding="utf-8") as fh:
            fh.write(contenido)
        print(f"  {nombre}: {len(contenido):,} bytes")


def actualizar_sprite(marca, firma):
    """Inserta o reemplaza i-marca e i-firma en el sprite del sitio."""
    (marca, vb_marca), (firma, vb_firma) = marca, firma
    sangrar = lambda t: "\n".join(("  " + l) if l.strip() else l for l in t.split("\n"))

    bloque = f'''  <!-- ======================================================================
       MARCA — monograma JQ entre etiquetas de código.

       Texto VECTORIZADO: no depende de que ninguna tipografía cargue, que es
       lo que se le exige a un logotipo. Con currentColor, una sola definición
       sirve para el navbar índigo y para el pie casi blanco, sin variantes.

       Monograma en DM Serif Display Italic, etiquetas en Archivo (ambas OFL).
       Se regenera con marca/generar.py.
       ====================================================================== -->
  <symbol id="i-marca" viewBox="{vb_marca}" fill="currentColor">
{sangrar(marca)}
  </symbol>

  <!-- Firma completa: marca, separador, nombre y rol. Para el pie. -->
  <symbol id="i-firma" viewBox="{vb_firma}" fill="currentColor">
{sangrar(firma)}
  </symbol>
'''

    texto = open(SPRITE, encoding="utf-8").read()

    # Primero se limpia lo que hubiera de una ejecución anterior, cada pieza
    # por su cuenta. Un solo patrón que fuera del comentario al último
    # </symbol> no vale: al ser no codicioso para en el PRIMER cierre, deja
    # atrás el segundo symbol y lo duplica en cada pasada.
    previos = len(re.findall(r'<symbol id="i-(?:marca|firma)"', texto))
    texto = re.sub(r"[ \t]*<!-- =+\s*\n[ \t]*MARCA —.*?-->[ \t]*\n?", "", texto, flags=re.DOTALL)
    texto = re.sub(r"[ \t]*<!-- Firma completa:.*?-->[ \t]*\n?", "", texto, flags=re.DOTALL)
    for pieza in ("i-marca", "i-firma"):
        texto = re.sub(rf'[ \t]*<symbol id="{pieza}".*?</symbol>[ \t]*\n?',
                       "", texto, flags=re.DOTALL)

    texto = texto.rstrip()
    assert texto.endswith("</svg>"), "El sprite no termina en </svg>"
    texto = texto[: -len("</svg>")].rstrip("\n") + "\n\n" + bloque + "</svg>\n"

    with open(SPRITE, "w", encoding="utf-8") as fh:
        fh.write(texto)

    # Red de seguridad: que quede exactamente una copia de cada pieza.
    n_marca = texto.count('<symbol id="i-marca"')
    n_firma = texto.count('<symbol id="i-firma"')
    assert n_marca == 1 and n_firma == 1, f"duplicados: {n_marca} marca, {n_firma} firma"

    accion = "actualizados" if previos else "añadidos"
    print(f"  icons.svg: symbols {accion} ({len(texto):,} bytes, "
          f"{previos} previos limpiados)")


def actualizar_paginas(vb_marca, vb_firma):
    """Sincroniza el viewBox de los <svg> del navbar y del pie en las páginas.

    Es obligatorio, no cosmético. El viewBox vive en el <symbol> del sprite,
    pero el <svg> que lo invoca con <use> NO lo hereda: para el navegador es
    una caja sin proporción intrínseca. Y un elemento reemplazado sin
    proporción, con `width: auto`, no vale 'lo que mida el dibujo' — vale el
    tamaño por defecto de la especificación, 300x150 px. El dibujo se escala
    a la altura pedida y se CENTRA dentro de esos 300px, así que aparecen
    ~115px de vacío a cada lado y el logotipo parece suelto del nombre.

    Poniendo aquí el mismo viewBox, el <svg> recupera su proporción y
    `width: auto` da el ancho exacto del dibujo.
    """
    import glob

    raiz = os.path.normpath(os.path.join(AQUI, "..", "..", ".."))
    paginas = ([os.path.join(raiz, "index.html"), os.path.join(raiz, "404.html")]
               + sorted(glob.glob(os.path.join(raiz, "views", "*.html"))))

    objetivos = {"brand__logo": vb_marca, "site-footer__signature": vb_firma}
    tocadas = 0

    for ruta in paginas:
        if not os.path.exists(ruta):
            continue
        texto = original = open(ruta, encoding="utf-8").read()

        for clase, vb in objetivos.items():
            def reemplazo(m, vb=vb, clase=clase):
                attrs = re.sub(r'\s*viewBox="[^"]*"', "", m.group(1))
                return f'<svg class="{clase}" viewBox="{vb}"{attrs}>'
            texto = re.sub(rf'<svg class="{clase}"(.*?)>', reemplazo, texto)

        if texto != original:
            with open(ruta, "w", encoding="utf-8") as fh:
                fh.write(texto)
            tocadas += 1

    print(f"  páginas sincronizadas: {tocadas}")


def generar_favicon(rutas):
    """A 16 px el </> es una mancha: el favicon lleva solo círculo y monograma."""
    ESCALA, LADO = 8, 64
    G = LADO * ESCALA

    img = Image.new("RGBA", (G, G), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margen, grosor = int(G * 0.030), int(G * 0.058)
    d.ellipse([margen, margen, G - margen, G - margen],
              outline=COLOR_FAVICON, width=grosor)

    fuente = ImageFont.truetype(rutas["dmserif.ttf"], int(G * 0.60))
    x0, y0, x1, y1 = d.textbbox((0, 0), "JQ", font=fuente)
    d.text(((G - (x1 - x0)) / 2 - x0, (G - (y1 - y0)) / 2 - y0), "JQ",
           font=fuente, fill=COLOR_FAVICON)

    destino = os.path.join(AQUI, "favicon.png")
    img.resize((LADO, LADO), Image.LANCZOS).save(destino, "PNG", optimize=True)
    print(f"  favicon.png: {LADO}x{LADO}, {os.path.getsize(destino):,} bytes")


if __name__ == "__main__":
    print("Tipografías:")
    rutas = asegurar_fuentes()
    print("Piezas:")
    marca, firma = construir(rutas)
    escribir_svgs(marca, firma)
    actualizar_sprite(marca, firma)
    actualizar_paginas(marca[1], firma[1])
    generar_favicon(rutas)
    print("\nListo.")
