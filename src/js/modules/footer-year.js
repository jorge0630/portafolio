/**
 * Mantiene actualizado el año del pie de página.
 *
 * El marcado lleva un año escrito a mano como respaldo, así que si el
 * JavaScript no se ejecuta se sigue viendo un año correcto en lugar de un
 * hueco vacío. Esto evita el problema que tenía el sitio, donde el año
 * estaba fijado y se quedó desfasado.
 */

export function initFooterYear() {
  const destino = document.querySelector('[data-anio]');
  if (!destino) return;

  destino.textContent = String(new Date().getFullYear());
}
