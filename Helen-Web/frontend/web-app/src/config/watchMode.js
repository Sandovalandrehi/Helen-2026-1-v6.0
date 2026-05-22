/**
 * Captura el flag ?watch=1 UNA sola vez, al evaluar los modulos (antes de
 * que React Router corra y borre el query string con su redireccion
 * inicial de "/" -> "/lock").
 *
 * Toda la app debe leer IS_WATCH_PI de aqui, nunca window.location.search
 * directamente, porque ese valor ya no es confiable despues de navegar.
 */
export const IS_WATCH_PI =
  new URLSearchParams(window.location.search).get('watch') === '1';
