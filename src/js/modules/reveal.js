/**
 * Revelado de elementos al entrar en pantalla.
 *
 * Reglas que se respetan aquí:
 *
 * · El contenido NUNCA se oculta si el JavaScript no corre. El estado
 *   inicial oculto lo aplica el CSS solo cuando este módulo ha marcado el
 *   documento con `data-js`, así que sin JS todo se ve desde el principio.
 *
 * · Solo se animan `opacity` y `transform`, que el navegador resuelve en la
 *   capa de composición. Nunca propiedades de layout.
 *
 * · Cada elemento se revela una sola vez y se deja de observar. Nada se
 *   mueve mientras el usuario está leyendo.
 *
 * · Con `prefers-reduced-motion` las duraciones valen 0.01ms (ver tokens),
 *   así que el elemento aparece sin desplazamiento y sin espera.
 */

const MARGEN = '0px 0px -12% 0px'; // dispara un poco antes del borde inferior

/* Se seleccionan los DOS atributos. `data-reveal` mueve al propio elemento;
   `data-reveal-group` deja quieto al contenedor y escalona a sus hijos. Un
   selector que solo mirase el primero dejaría los grupos sin observar y,
   como el CSS ya los oculta, invisibles de forma permanente. */
const SELECTOR = '[data-reveal], [data-reveal-group]';

export function initReveal() {
  const objetivos = document.querySelectorAll(SELECTOR);
  if (objetivos.length === 0) return;

  // A partir de aquí el CSS puede ocultar los elementos con seguridad:
  // sabemos que hay JavaScript para volver a mostrarlos.
  document.documentElement.dataset.js = 'true';

  const mostrar = (el) => {
    el.dataset.revealed = 'true';
  };

  // Sin soporte de IntersectionObserver, todo visible de golpe.
  if (!('IntersectionObserver' in window)) {
    objetivos.forEach(mostrar);
    return;
  }

  const observador = new IntersectionObserver(
    (entradas, obs) => {
      for (const entrada of entradas) {
        if (!entrada.isIntersecting) continue;
        mostrar(entrada.target);
        obs.unobserve(entrada.target);
      }
    },
    { rootMargin: MARGEN, threshold: 0.01 }
  );

  objetivos.forEach((el) => {
    /* Los grupos escalonan a sus hijos: cada uno recibe el índice que el
       CSS convierte en retardo. Se hace aquí y no a mano en el HTML para
       que añadir o quitar elementos no obligue a renumerar nada. */
    if (el.hasAttribute('data-reveal-group')) {
      [...el.children].forEach((hijo, i) => {
        hijo.style.setProperty('--reveal-index', String(i));
      });
    }
    observador.observe(el);
  });

  /* Si la página carga ya desplazada (por ejemplo con un ancla en la URL),
     lo que quede por encima del pliegue se muestra sin animación. */
  requestAnimationFrame(() => {
    objetivos.forEach((el) => {
      if (el.getBoundingClientRect().top < 0) mostrar(el);
    });
  });

  /* Seguro. El observador puede no llegar a entregar nada: pestaña en
     segundo plano al cargar, un fallo del navegador, una extensión que
     interfiera. En ese caso el contenido se quedaría invisible, que es
     mucho peor que perderse la animación. A los 3 segundos se revela todo
     lo que siga pendiente. */
  window.setTimeout(() => {
    objetivos.forEach((el) => {
      if (!el.dataset.revealed) mostrar(el);
    });
  }, 3000);
}
