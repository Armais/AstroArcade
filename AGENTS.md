# Web de Astro Arcade — instrucciones para agentes

La web del estudio (astroarcade.es): HTML y CSS escritos a mano, sin compilar, servida por Hostinger.
En español, con su copia en inglés en `en/`: todo cambio de texto va a las dos.

## Novedades: una entrada por cada versión publicada de un juego

Cada versión que sale a los jugadores (Google Play, itch.io o la web) lleva su entrada, igual que sus
notas en Google Play e itch.io. Lo piden también el `AGENTS.md` o `CLAUDE.md` raíz de cada juego.

1. Un JSON en `tools/novedades/entradas/<juego>-<versión>.json`, en español e inglés. El formato está
   en la cabecera de `tools/novedades/generar.py`. `juego` es una clave de `JUEGOS` en ese script: un
   juego nuevo se añade allí primero (nombre, páginas, Google Play y prueba cerrada).
2. Los cambios cuentan lo que nota el jugador desde la entrada anterior de ese juego, sacado de los
   commits de `main` del juego, sin jerga interna (`NET_VERSION`, dethash, migraciones, pruebas…). Si
   salen varias versiones sin entrada, va una sola con la última que lo recoge todo. Una build que no
   cambia nada para el jugador no lleva entrada.
3. Los nombres de minijuegos, botones y opciones son los del juego en cada idioma (en sus catálogos,
   p. ej. `src/core/idiomas/en.cpp` en Orbit Rivals y Pinball Master, `assets/text/en.json` en Cotton
   vs Ants). En los cambios solo vale `**negrita**`.
4. `python3 tools/novedades/generar.py` rehace la lista (`novedades/`, `en/news/`), la página de cada
   entrada, las tres últimas de las portadas y el sitemap. `--comprobar` sale con 1 si falta generar.
5. Mirar las páginas en el navegador (escritorio y móvil) y hacer commit del JSON con lo generado.

- `"prueba_cerrada": true` añade la invitación a la prueba cerrada de Google Play (el grupo de testers y
  el enlace `prueba` del juego en `JUEGOS`). Cuando el juego salga para todos, se quita, y su enlace
  de la tienda va en `google_play`.
- Lo generado no se edita a mano: las carpetas `novedades/` y `en/news/` y lo que hay entre
  `<!-- novedades:inicio -->` y `<!-- novedades:fin -->` en `index.html` y `en/index.html`. Se cambia el
  JSON o el script y se regenera.

## Caché

Al cambiar `css/site.css` o un `js/*.js`, se sube su `?v=` en todas las páginas (lo explica
`.htaccess`). El generador copia esas versiones de `index.html`, así que después se regenera.
