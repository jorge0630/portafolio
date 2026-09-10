/**
 * Galería de capturas con lightbox.
 *
 * Reemplaza al antiguo src/js/gallery.js, que tenía dos problemas:
 *
 * 1. Registraba el listener de teclado en `document` sin comprobar si el
 *    modal estaba abierto. Pulsar → nada más cargar la página calculaba
 *    `(0 + 1) % 0` → NaN, asignaba `undefined` al src y el navegador pedía
 *    /views/undefined (404). Además dejaba el índice contaminado como NaN,
 *    así que la siguiente apertura también fallaba.
 *
 * 2. Construía el array por orden del DOM con push(), pero leía el índice
 *    del atributo `data-index`. Coincidían por casualidad: al reordenar las
 *    imágenes sin renumerar, el modal abría la equivocada sin dar ningún
 *    error.
 *
 * Aquí el orden lo determina únicamente el DOM y las teclas se escuchan en
 * el propio <dialog>, que al ser modal solo recibe eventos mientras está
 * abierto. Los dos fallos dejan de ser posibles por construcción.
 */

export function initGallery() {
  const dialogo = document.querySelector('#lightbox');
  const disparadores = [...document.querySelectorAll('[data-lightbox]')];

  if (!dialogo || disparadores.length === 0) return;

  const imagen = dialogo.querySelector('[data-lightbox-img]');
  const pie = dialogo.querySelector('[data-lightbox-caption]');
  const contador = dialogo.querySelector('[data-lightbox-count]');
  const btnCerrar = dialogo.querySelector('[data-lightbox-close]');
  const btnPrev = dialogo.querySelector('[data-lightbox-prev]');
  const btnNext = dialogo.querySelector('[data-lightbox-next]');

  // El orden es el del DOM. No hay ningún data-index que mantener al día.
  const laminas = disparadores.map((boton) => {
    const img = boton.querySelector('img');
    return { src: img.currentSrc || img.src, alt: img.alt };
  });

  const total = laminas.length;
  let indice = 0;

  // Con una sola imagen se ocultan los controles de navegación (lo gestiona
  // el CSS a partir de este atributo).
  dialogo.dataset.unica = String(total === 1);

  const mostrar = (i) => {
    // El módulo aritmético con `+ total` hace que el índice dé la vuelta en
    // ambos sentidos sin salirse nunca del rango.
    indice = (i + total) % total;
    const lamina = laminas[indice];

    imagen.src = lamina.src;
    imagen.alt = lamina.alt;
    if (pie) pie.textContent = lamina.alt;
    if (contador) contador.textContent = `${indice + 1} / ${total}`;
  };

  /* --- Apertura -------------------------------------------------------- */

  disparadores.forEach((boton, i) => {
    boton.addEventListener('click', () => {
      mostrar(i);
      dialogo.showModal();
    });
  });

  /* --- Navegación ------------------------------------------------------ */

  btnPrev?.addEventListener('click', () => mostrar(indice - 1));
  btnNext?.addEventListener('click', () => mostrar(indice + 1));
  btnCerrar?.addEventListener('click', () => dialogo.close());

  /* El listener va en el <dialog> y no en `document`: al abrirse con
     showModal() el foco queda atrapado dentro, así que estas teclas solo
     pueden llegar aquí mientras está abierto. `Escape` lo gestiona el
     propio elemento de forma nativa. */
  dialogo.addEventListener('keydown', (evento) => {
    if (total < 2) return;

    if (evento.key === 'ArrowRight') {
      evento.preventDefault();
      mostrar(indice + 1);
    } else if (evento.key === 'ArrowLeft') {
      evento.preventDefault();
      mostrar(indice - 1);
    }
  });

  /* Clic en el fondo. El objetivo es el propio <dialog> solo cuando se
     pulsa fuera de la figura, porque esta ocupa únicamente su contenido. */
  dialogo.addEventListener('click', (evento) => {
    if (evento.target === dialogo) dialogo.close();
  });
}
