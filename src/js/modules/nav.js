/**
 * Navegación principal: menú móvil y sombra del header al hacer scroll.
 *
 * Todo el estado visual se deriva de `aria-expanded`, de modo que el
 * atributo accesible y lo que se ve en pantalla no pueden desincronizarse:
 * no existe una variable aparte que pueda quedar desfasada.
 */

const BREAKPOINT_ESCRITORIO = '(min-width: 48em)';

export function initNav() {
  const toggle = document.querySelector('#nav-toggle');
  const nav = document.querySelector('#nav-menu');

  // Si el marcado no está en esta página, no se hace nada. Las vistas de
  // proyecto tienen header pero no menú desplegable, y ahí este módulo
  // simplemente no actúa. La sombra del header vive en header.js
  // precisamente para que sí funcione en esas páginas.
  if (!toggle || !nav) return;

  const estaAbierto = () => toggle.getAttribute('aria-expanded') === 'true';

  const setAbierto = (abierto) => {
    toggle.setAttribute('aria-expanded', String(abierto));
    toggle.setAttribute(
      'aria-label',
      abierto ? 'Cerrar menú de navegación' : 'Abrir menú de navegación'
    );
    nav.dataset.open = String(abierto);
  };

  const cerrar = () => {
    if (estaAbierto()) setAbierto(false);
  };

  // Estado inicial explícito
  setAbierto(false);

  /* --- Interacciones -------------------------------------------------- */

  toggle.addEventListener('click', () => setAbierto(!estaAbierto()));

  // Al elegir un destino, el menú sobra
  nav.addEventListener('click', (evento) => {
    if (evento.target.closest('a')) cerrar();
  });

  // Escape cierra y devuelve el foco al botón, para no perder al usuario
  // de teclado en mitad del documento.
  document.addEventListener('keydown', (evento) => {
    if (evento.key === 'Escape' && estaAbierto()) {
      cerrar();
      toggle.focus();
    }
  });

  // Clic fuera del menú
  document.addEventListener('click', (evento) => {
    if (!estaAbierto()) return;
    if (nav.contains(evento.target) || toggle.contains(evento.target)) return;
    cerrar();
  });

  // Al pasar a escritorio el panel deja de existir como tal: se limpia el
  // estado para no volver a móvil con el menú "abierto" de forma invisible.
  window.matchMedia(BREAKPOINT_ESCRITORIO).addEventListener('change', (evento) => {
    if (evento.matches) cerrar();
  });
}
