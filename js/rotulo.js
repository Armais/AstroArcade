// El rotulo de neon de Astro Arcade encendiendose, como en la pantalla de arranque de Orbit Rivals
// (OrbitRivals/src/ui/screen_menu.cpp). Las capas y sus sitios son los de assets/textures/estudio.txt
// y los tiempos, los de su tabla ENCENDIDO: nunca mas de 3 destellos por segundo. Con movimiento
// reducido no hay destellos: cada pieza sube poco a poco. Al pulsar el rotulo vuelve a encenderse.
(function () {
  "use strict";

  // Las rutas salen de donde esta este fichero, para que valga igual en / que en /en/
  var RAIZ = new URL("../", document.currentScript.src);

  var LIENZO = [886, 619];
  // pieza, x, y, ancho, alto en el atlas; x, y en el lienzo. Se pintan en este orden.
  var CAPAS = [
    ["apagado", 1056, 0, 721, 475, 83, 80],
    ["a1", 0, 0, 520, 541, 54, 0],
    ["a2", 528, 0, 520, 541, 307, 0],
    ["anillo", 722, 549, 843, 357, 0, 130],
    ["planeta", 1573, 549, 217, 217, 669, 188],
    ["astro", 0, 938, 379, 182, 77, 436],
    ["arcade", 387, 938, 430, 181, 377, 438],
    ["a1", 0, 549, 353, 381, 138, 80],
    ["a2", 361, 549, 353, 381, 390, 80],
    ["anillo", 825, 938, 689, 175, 83, 217],
    ["planeta", 1522, 938, 53, 53, 751, 270],
    ["astro", 1583, 938, 270, 50, 128, 505],
    ["arcade", 0, 1128, 327, 50, 426, 505]
  ];
  // destello [t0, t1, nivel], sube, fijo, tartamudeo [t0, t1, nivel]
  var ENCENDIDO = {
    a1: [[0.50, 0.58, 1.0], 0.76, 1.08],
    a2: [[0.98, 1.05, 1.0], 1.14, 1.44],
    anillo: [[1.58, 1.64, 1.0], 1.76, 2.06],
    planeta: [[2.14, 2.18, 1.0], 2.22, 2.42],
    astro: [[2.44, 2.50, 1.0], 2.54, 2.76],
    arcade: [[2.70, 2.76, 0.7], 2.88, 3.14, [3.52, 3.60, 0.35]]
  };
  var ENTRA = 0.35, FIN = 3.7;
  // El zumbido (sfx logo_neon) sale con el primer destello, como BOOT_SFX_AT; si se vuelve a
  // encender a medias, el anterior se corta con un fundido de 120 ms, como al saltar el logo
  var SONIDO_EN = 0.50, CORTE = 0.12;

  // Lo de debajo del rotulo (lema y botones) sale cuando se enciende ARCADE; si algo falla, ya
  var LEMA_EN = 2.9;
  var portada = document.querySelector(".portada");
  function mostrarLema() { if (portada) portada.classList.add("encendida"); }
  setTimeout(mostrarLema, 6000);

  var canvas = document.getElementById("rotulo");
  if (!canvas || !canvas.getContext) { mostrarLema(); return; }
  var ctx = canvas.getContext("2d");
  var boton = canvas.closest("button");
  var reducido = window.matchMedia("(prefers-reduced-motion: reduce)");
  var atlas = new Image();
  var inicio = 0, pedido = 0;

  function sat(x) { return x < 0 ? 0 : x > 1 ? 1 : x; }

  function nivel(pieza, t) {
    var en = ENCENDIDO[pieza];
    if (!en) return 1; // lo apagado se ve siempre
    var d = en[0], sube = en[1], fijo = en[2], tt = en[3];
    if (reducido.matches) return sat((t - d[0]) / (fijo - d[0]));
    if (t >= d[0] && t < d[1]) return d[2];
    if (tt && t >= tt[0] && t < tt[1]) return tt[2];
    return sat((t - sube) / (fijo - sube));
  }

  function ajustar() {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w = Math.round(canvas.clientWidth * dpr);
    var h = Math.round(canvas.clientHeight * dpr);
    if (w && h && (canvas.width !== w || canvas.height !== h)) {
      canvas.width = w;
      canvas.height = h;
    }
  }

  function pintar(t) {
    var s = canvas.width / LIENZO[0];
    var a = sat(t / ENTRA);
    a = a * a * (3 - 2 * a);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (var i = 0; i < CAPAS.length; i++) {
      var c = CAPAS[i];
      var k = nivel(c[0], t);
      if (k <= 0) continue;
      ctx.globalAlpha = a * k;
      ctx.drawImage(atlas, c[1], c[2], c[3], c[4], c[5] * s, c[6] * s, c[3] * s, c[4] * s);
    }
    ctx.globalAlpha = 1;
  }

  function cuadro(ahora) {
    var t = (ahora - inicio) / 1000;
    pintar(Math.min(t, FIN));
    if (t >= LEMA_EN) mostrarLema();
    pedido = t < FIN ? requestAnimationFrame(cuadro) : 0;
  }

  function encender() {
    cancelAnimationFrame(pedido);
    ajustar();
    inicio = performance.now();
    pedido = requestAnimationFrame(cuadro);
  }

  // Los navegadores no dejan sonar nada hasta que se pulsa algo: el sonido va solo con el clic.
  // Web Audio y no <audio> para que salga a su hora exacta tambien en el iPhone.
  var audio = null, zumbido = null, sonando = null, vez = 0;

  function sonar() {
    var AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return;
    if (!audio) {
      audio = new AC();
      zumbido = fetch(new URL("audio/rotulo.mp3", RAIZ))
        .then(function (r) { return r.arrayBuffer(); })
        .then(function (b) { return new Promise(function (ok, mal) { audio.decodeAudioData(b, ok, mal); }); });
    }
    audio.resume();
    if (sonando) {
      var ahora = audio.currentTime;
      sonando.gain.gain.setValueAtTime(sonando.gain.gain.value, ahora);
      sonando.gain.gain.linearRampToValueAtTime(0, ahora + CORTE);
      sonando.fuente.stop(ahora + CORTE);
      sonando = null;
    }
    var mia = ++vez, cuando = audio.currentTime + SONIDO_EN;
    zumbido.then(function (buffer) {
      if (mia !== vez) return;
      var fuente = audio.createBufferSource(), gain = audio.createGain();
      fuente.buffer = buffer;
      fuente.connect(gain).connect(audio.destination);
      var tarde = audio.currentTime - cuando;   // si el fichero tardo en llegar, va por donde toca
      if (tarde > 0) fuente.start(0, tarde); else fuente.start(cuando);
      sonando = { fuente: fuente, gain: gain };
    }).catch(function () {});
  }

  atlas.onload = encender;
  atlas.onerror = mostrarLema;
  atlas.src = new URL("img/rotulo.webp", RAIZ).href;

  if (boton) boton.addEventListener("click", function () { encender(); sonar(); });
  window.addEventListener("resize", function () {
    ajustar();
    if (!pedido && atlas.complete) pintar(FIN);
  });
})();
