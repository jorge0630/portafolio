/**
 * Formulario de contacto.
 *
 * Envía a Formspree por fetch para no sacar al usuario de la página. Si el
 * JavaScript falla o no llega a cargar, el <form> conserva su `action` y su
 * `method`, así que el envío sigue funcionando de forma nativa: la mejora es
 * progresiva, no un requisito.
 */

const MENSAJES = {
  enviando: 'Enviando…',
  exito: '¡Tu mensaje fue enviado con éxito! Te responderé pronto.',
  errorServidor: 'Hubo un problema al enviar el mensaje. Inténtalo de nuevo.',
  errorRed: 'No se pudo conectar. Revisa tu conexión e inténtalo más tarde.',
};

export function initContactForm() {
  const formulario = document.querySelector('#contact-form');
  if (!formulario) return;

  const mensaje = formulario.querySelector('#form-message');
  const boton = formulario.querySelector('#form-submit');
  const textoBoton = boton?.querySelector('[data-texto]');
  const trampa = formulario.querySelector('[name="_gotcha"]');

  const textoOriginal = textoBoton?.textContent ?? 'Enviar mensaje';

  const mostrar = (texto, estado) => {
    if (!mensaje) return;
    mensaje.textContent = texto;
    mensaje.dataset.estado = estado;
  };

  const limpiar = () => {
    if (!mensaje) return;
    mensaje.textContent = '';
    delete mensaje.dataset.estado;
  };

  const cargando = (activo) => {
    if (!boton) return;
    boton.disabled = activo;
    boton.dataset.cargando = String(activo);
    if (textoBoton) textoBoton.textContent = activo ? MENSAJES.enviando : textoOriginal;
  };

  formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();

    /* Trampa anti-spam: el campo está fuera de pantalla, así que solo lo
       rellena un bot que completa todos los campos del formulario. Se finge
       un envío correcto para no darle pistas de que fue detectado. */
    if (trampa?.value) {
      formulario.reset();
      mostrar(MENSAJES.exito, 'exito');
      return;
    }

    // Un envío nuevo no debe dejar visible el resultado del anterior
    limpiar();
    cargando(true);

    try {
      const respuesta = await fetch(formulario.action, {
        method: 'POST',
        body: new FormData(formulario),
        headers: { Accept: 'application/json' },
      });

      if (respuesta.ok) {
        formulario.reset();
        mostrar(MENSAJES.exito, 'exito');
      } else {
        mostrar(MENSAJES.errorServidor, 'error');
      }
    } catch {
      // Solo entra aquí si la petición no llegó a completarse (sin red,
      // DNS caído, CORS). Los errores del servidor van por la rama de arriba.
      mostrar(MENSAJES.errorRed, 'error');
    } finally {
      cargando(false);
    }
  });
}
