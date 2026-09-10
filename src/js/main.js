/**
 * Punto de entrada del sitio.
 *
 * Se carga con <script type="module">, que ya se difiere por defecto: el
 * DOM está listo cuando esto se ejecuta, así que no hace falta envolverlo
 * en un DOMContentLoaded.
 *
 * Cada módulo comprueba por su cuenta si su marcado existe en la página,
 * de modo que este mismo archivo sirve para el index y para las vistas de
 * proyecto sin condicionales.
 */

import { initHeader } from './modules/header.js';
import { initNav } from './modules/nav.js';
import { initReveal } from './modules/reveal.js';
import { initCarousels } from './modules/carousel.js';
import { initGallery } from './modules/gallery.js';
import { initContactForm } from './modules/contact-form.js';
import { initFooterYear } from './modules/footer-year.js';

initHeader();        // las 6 páginas
initNav();           // solo el index
initReveal();        // las 6 páginas
initCarousels();     // carruseles, si los hubiera
initGallery();       // solo las vistas de proyecto
initContactForm();   // solo el index
initFooterYear();    // las 6 páginas
