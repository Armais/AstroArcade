// Astro Arcade: el video de la portada, los trailers y el visor de capturas. Sin dependencias:
// sin JavaScript la portada se queda con la imagen fija, los trailers abren YouTube y las capturas se abren solas.
(function () {
  "use strict";
  var ingles = document.documentElement.lang === "en";

  // En Android, lo primero es instalarlo desde Google Play; en iPhone y en el PC, jugar en el navegador
  if (/Android/i.test(navigator.userAgent)) document.documentElement.classList.add("android");

  // Video de la portada: no arranca si se han pedido menos animaciones o ahorro de datos
  // (se queda la imagen fija) y se para mientras no se ve
  var fondo = document.querySelector(".portada-video video");
  var quieto = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var ahorro = navigator.connection && navigator.connection.saveData;
  if (fondo && !quieto && !ahorro) {
    var reproducir = function () {
      var p = fondo.play();
      if (p && p.catch) p.catch(function () {});
    };
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (cambios) {
        if (cambios[0].isIntersecting) reproducir(); else fondo.pause();
      }).observe(fondo);
    } else {
      reproducir();
    }
  }

  // Trailers: hasta que se pulsa no se pide nada a YouTube (ni su reproductor ni sus cookies)
  document.querySelectorAll("[data-youtube]").forEach(function (caja) {
    var enlace = caja.querySelector("a");
    if (!enlace) return;
    enlace.addEventListener("click", function (ev) {
      ev.preventDefault();
      var video = document.createElement("iframe");
      video.src = "https://www.youtube-nocookie.com/embed/" + caja.getAttribute("data-youtube") +
        "?autoplay=1&rel=0&hl=" + (ingles ? "en" : "es");
      video.title = enlace.getAttribute("aria-label") || "Trailer";
      video.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
      caja.replaceChildren(video);
      video.focus();
    });
  });

  // Visor de capturas: la grande encima de la pagina; se cierra con Esc, con la X o tocando fuera
  var capturas = document.querySelectorAll(".galeria a");
  if (capturas.length && window.HTMLDialogElement) {
    var visor = document.createElement("dialog");
    visor.className = "visor";
    var grande = document.createElement("img");
    var cerrar = document.createElement("button");
    cerrar.type = "button";
    cerrar.className = "visor-cerrar";
    cerrar.textContent = "×";
    cerrar.setAttribute("aria-label", ingles ? "Close" : "Cerrar");
    visor.append(grande, cerrar);
    document.body.appendChild(visor);
    visor.addEventListener("click", function () { visor.close(); });
    visor.addEventListener("close", function () { grande.removeAttribute("src"); });

    capturas.forEach(function (enlace) {
      enlace.addEventListener("click", function (ev) {
        ev.preventDefault();
        grande.src = enlace.href;
        grande.alt = enlace.querySelector("img").alt;
        visor.showModal();
      });
    });
  }
})();
