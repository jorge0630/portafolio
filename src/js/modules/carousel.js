/**
 * Carrusel de capturas. Sustituye a Swiper.
 *
 * El desplazamiento lo hace el navegador con CSS Scroll Snap; este módulo
 * solo mueve el scroll al pulsar los controles y mantiene sincronizados los
 * indicadores. Esa división es lo que permite que, si el JavaScript falla,
 * el carrusel siga siendo desplazable con el dedo o la rueda del ratón.
 *
 * Marcado esperado:
 *
 *   <div class="carousel" data-carousel>
 *     <div class="carousel__track">
 *       <figure class="carousel__slide">…</figure>
 *     </div>
 *     <button data-carousel-prev>…</button>
 *     <button data-carousel-next>…</button>
 *     <div class="carousel__dots"></div>   ← los puntos se generan aquí
 *   </div>
 */

export function initCarousels() {
  document.querySelectorAll('[data-carousel]').forEach(montar);
}

function montar(carrusel) {
  const pista = carrusel.querySelector('.carousel__track');
  const anterior = carrusel.querySelector('[data-carousel-prev]');
  const siguiente = carrusel.querySelector('[data-carousel-next]');
  const contenedorPuntos = carrusel.querySelector('.carousel__dots');

  if (!pista) return;

  const laminas = [...pista.children];

  /* Con una sola imagen no hay nada que navegar. Se retiran los controles
     en lugar de dejarlos inertes: el sitio anterior mostraba flechas y un
     punto de paginación que no hacían nada en los proyectos de una sola
     captura. */
  if (laminas.length < 2) {
    anterior?.remove();
    siguiente?.remove();
    contenedorPuntos?.remove();
    pista.removeAttribute('tabindex');
    pista.removeAttribute('role');
    return;
  }

  let indice = 0;

  /* --- Indicadores ---------------------------------------------------- */

  const puntos = laminas.map((_, i) => {
    const punto = document.createElement('button');
    punto.type = 'button';
    punto.className = 'carousel__dot';
    punto.setAttribute('aria-label', `Ir a la imagen ${i + 1} de ${laminas.length}`);
    punto.addEventListener('click', () => irA(i));
    contenedorPuntos?.append(punto);
    return punto;
  });

  /* --- Sincronización -------------------------------------------------- */

  const sincronizar = (nuevo) => {
    indice = nuevo;

    puntos.forEach((punto, i) => {
      // aria-current en lugar de una clase: el estado queda expuesto a los
      // lectores de pantalla, no solo pintado.
      if (i === indice) punto.setAttribute('aria-current', 'true');
      else punto.removeAttribute('aria-current');
    });

    // Sin bucle: en los extremos se desactiva el control correspondiente.
    if (anterior) anterior.disabled = indice === 0;
    if (siguiente) siguiente.disabled = indice === laminas.length - 1;
  };

  /* Se desplaza la pista, no el elemento: scrollIntoView también movería la
     página en vertical para traer la lámina a la vista, y pulsar "siguiente"
     no debería mover el scroll de la página.

     El destino se calcula respecto a la primera lámina en lugar de usar
     offsetLeft a secas, porque offsetLeft es relativo al ancestro
     posicionado (.carousel), no a la pista. */
  const irA = (i) => {
    const destino = Math.max(0, Math.min(i, laminas.length - 1));
    const izquierda = laminas[destino].offsetLeft - laminas[0].offsetLeft;

    pista.scrollTo({
      left: izquierda,
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches
        ? 'auto'
        : 'smooth',
    });
  };

  anterior?.addEventListener('click', () => irA(indice - 1));
  siguiente?.addEventListener('click', () => irA(indice + 1));

  /* La lámina visible se detecta observando cuál ocupa la pista, y no
     calculando scrollLeft. Así el estado es correcto venga el movimiento de
     donde venga: botones, gesto táctil, rueda o teclado. */
  const observador = new IntersectionObserver(
    (entradas) => {
      for (const entrada of entradas) {
        if (entrada.isIntersecting) {
          sincronizar(laminas.indexOf(entrada.target));
        }
      }
    },
    { root: pista, threshold: 0.6 }
  );

  laminas.forEach((lamina) => observador.observe(lamina));

  sincronizar(0);
}
