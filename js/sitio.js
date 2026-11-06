// Astro Arcade: la barra fija de la portada, los trailers y el visor de capturas. Sin dependencias:
// sin JavaScript la portada tiene su menu, los trailers abren YouTube y las capturas se abren solas.
(function () {
  "use strict";
  var ingles = document.documentElement.lang === "en";

  // La barra de la portada sale cuando sus botones se van por arriba: el Jugar de la barra los releva
  var barra = document.querySelector(".barra[data-tras-portada]");
  var botones = document.querySelector(".portada-botones");
  if (barra && botones && "IntersectionObserver" in window) {
    new IntersectionObserver(function (cambios) {
      var c = cambios[0];
      barra.classList.toggle("visible", !c.isIntersecting && c.boundingClientRect.top < 0);
    }).observe(botones);
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
