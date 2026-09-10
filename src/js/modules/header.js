/**
 * Sombra del header al hacer scroll.
 *
 * Vive aparte de nav.js porque el header existe en las 6 páginas, mientras
 * que el menú desplegable solo está en el index: si esto siguiera dentro de
 * nav.js, las vistas de proyecto se quedarían sin el efecto, ya que ese
 * módulo sale antes al no encontrar el botón hamburguesa.
 *
 * Solo escribe un atributo; el aspecto lo decide el CSS.
 */

export function initHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const actualizar = () => {
    header.dataset.scrolled = String(window.scrollY > 8);
  };

  actualizar();
  window.addEventListener('scroll', actualizar, { passive: true });
}
