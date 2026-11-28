#!/usr/bin/env python3
"""Novedades de la web de Astro Arcade: una entrada por cada version publicada de un juego.

Cada entrada es un JSON en tools/novedades/entradas/<juego>-<version>.json, en espanol y en ingles:

    {
      "juego": "orbit-rivals",            # una clave de JUEGOS (abajo)
      "version": "1.3.0",                 # la que ve el jugador
      "fecha": "2026-11-23",              # el dia que se publico (AAAA-MM-DD)
      "prueba_cerrada": true,             # opcional: invita a la prueba cerrada de Google Play
      "es": {"titulo": "...", "cambios": ["**Lo nuevo:** contado para el jugador.", "..."]},
      "en": {"titulo": "...", "cambios": ["..."]}
    }

En los cambios solo vale **negrita**; lo demas se escribe tal cual (se escapa).

    python3 tools/novedades/generar.py              # rehace las paginas, la portada y el sitemap
    python3 tools/novedades/generar.py --comprobar  # sale con 1 si algo no esta al dia (no escribe)

Lo que rehace, siempre entero a partir de las entradas:
  - novedades/index.html y en/news/index.html: la lista, de la mas nueva a la mas vieja;
  - novedades/<juego>-<version>/ y en/news/<juego>-<version>/: una pagina por entrada;
  - en index.html y en/index.html, lo que hay entre <!-- novedades:inicio --> y <!-- novedades:fin -->:
    las tres ultimas;
  - en sitemap.xml, las direcciones de las novedades (y la fecha de la portada si una entrada es mas nueva).
Las versiones del CSS y del JS (?v=) y el ano del pie se copian de index.html.
Solo usa la biblioteca estandar de Python 3.
"""
import datetime
import html
import json
import posixpath
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ENTRADAS = Path(__file__).resolve().parent / "entradas"
WEB = "https://astroarcade.es/"
GRUPO_TESTERS = "https://groups.google.com/g/astroarcade-testers"
EN_PORTADA = 3

# Las rutas son desde la raiz de la web, sin la barra del principio
JUEGOS = {
    "orbit-rivals": {
        "nombre": "Orbit Rivals",
        "es": {"pagina": "orbit-rivals/", "jugar": "orbit-rivals/jugar/"},
        "en": {"pagina": "en/orbit-rivals/", "jugar": "en/orbit-rivals/play/"},
        "google_play": "https://play.google.com/store/apps/details?id=com.astroarcade.orbitrivals",
        "prueba": None,
    },
    "cotton-vs-ants": {
        "nombre": "Cotton vs Ants",
        "es": {"pagina": "cotton-vs-ants/", "jugar": "cotton-vs-ants/jugar/"},
        "en": {"pagina": "en/cotton-vs-ants/", "jugar": "en/cotton-vs-ants/play/"},
        "google_play": None,
        "prueba": "https://play.google.com/apps/testing/com.astroarcade.cottonvsants",
    },
    "spin-brawl": {
        "nombre": "Spin Brawl",
        "es": {"pagina": "spin-brawl/", "jugar": "spin-brawl/jugar/"},
        "en": {"pagina": "en/spin-brawl/", "jugar": "en/spin-brawl/play/"},
        "google_play": None,
        "prueba": None,
    },
    "pinball-master": {
        "nombre": "Pinball Master",
        "es": {"pagina": "pinball-master/", "jugar": "pinball-master/jugar/"},
        "en": {"pagina": "en/pinball-master/", "jugar": "en/pinball-master/play/"},
        "google_play": None,
        "prueba": "https://play.google.com/apps/testing/com.astroarcade.pinballmaster",
    },
}

TXT = {
    "es": {
        "lang": "es",
        "inicio": "",
        "lista": "novedades/",
        "prensa": "prensa/",
        "privacidad": "privacidad/",
        "ancla_juegos": "#juegos", "ancla_nosotros": "#nosotros", "ancla_contacto": "#contacto",
        "menu": "Menú", "juegos": "Juegos", "novedades": "Novedades", "nosotros": "Nosotros",
        "prensa_txt": "Prensa", "contacto": "Contacto", "privacidad_txt": "Privacidad", "jugar": "Jugar",
        "otro_idioma": "EN", "otro_idioma_nombre": "English", "otro_lang": "en",
        "titulo_lista": "Novedades",
        "entradilla": "Lo nuevo de cada versión de nuestros juegos.",
        "desc_lista": "Lo nuevo de cada versión de los juegos de Astro Arcade: Orbit Rivals, Cotton vs Ants, Spin Brawl y Pinball Master.",
        "ver_todas": "Ver todas las novedades",
        "volver": "← Todas las novedades",
        "desc_entrada": "Lo nuevo en {juego} {version}: {titulo}.",
        "jugar_gratis": "Jugar gratis",
        "detalles": "Capturas y detalles",
        "play_alt": "Disponible en Google Play", "play_img": "img/google-play-es.png", "play_campana": "novedades_es",
        "marca_play": " Google Play y el logotipo de Google Play son marcas de Google LLC.",
        "prueba_titulo": "Pruébalo en Android antes que nadie",
        "prueba_intro": "{juego} está en prueba cerrada en Google Play y puede apuntarse cualquiera:",
        "prueba_pasos": [
            'Únete al <a href="{grupo}">grupo de testers de Astro Arcade</a>.',
            'Con la misma cuenta de Google, abre <a href="{prueba}">la página de la prueba</a> y hazte tester.',
            "Instálalo desde Google Play.",
        ],
        "prueba_final": "Si puedes, tenlo instalado al menos 14 días: Google lo pide para que el juego salga para todos.",
        "meses": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
                  "octubre", "noviembre", "diciembre"],
        "locale": "es_ES",
    },
    "en": {
        "lang": "en",
        "inicio": "en/",
        "lista": "en/news/",
        "prensa": "en/press/",
        "privacidad": "en/privacy/",
        "ancla_juegos": "#games", "ancla_nosotros": "#about", "ancla_contacto": "#contact",
        "menu": "Menu", "juegos": "Games", "novedades": "News", "nosotros": "About",
        "prensa_txt": "Press", "contacto": "Contact", "privacidad_txt": "Privacy", "jugar": "Play",
        "otro_idioma": "ES", "otro_idioma_nombre": "Español", "otro_lang": "es",
        "titulo_lista": "News",
        "entradilla": "What’s new in every version of our games.",
        "desc_lista": "What’s new in every version of Astro Arcade’s games: Orbit Rivals, Cotton vs Ants, Spin Brawl and Pinball Master.",
        "ver_todas": "See all news",
        "volver": "← All news",
        "desc_entrada": "What’s new in {juego} {version}: {titulo}.",
        "jugar_gratis": "Play free",
        "detalles": "Screenshots and details",
        "play_alt": "Get it on Google Play", "play_img": "img/google-play-en.png", "play_campana": "novedades_en",
        "marca_play": " Google Play and the Google Play logo are trademarks of Google LLC.",
        "prueba_titulo": "Try it on Android before anyone else",
        "prueba_intro": "{juego} is in closed testing on Google Play, and anyone can join:",
        "prueba_pasos": [
            'Join the <a href="{grupo}">Astro Arcade testers group</a>.',
            'With the same Google account, open <a href="{prueba}">the test page</a> and become a tester.',
            "Install it from Google Play.",
        ],
        "prueba_final": "If you can, keep it installed for at least 14 days: Google needs that before the game can be released to everyone.",
        "meses": ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                  "October", "November", "December"],
        "locale": "en_US",
    },
}

REDES = [
    ("Discord", "https://discord.gg/VyT2ESFKJc"),
    ("TikTok", "https://www.tiktok.com/@astro_arcade_games"),
    ("Instagram", "https://www.instagram.com/orbit.rivals/"),
    ("YouTube", "https://www.youtube.com/@OrbitRivalsGame"),
    ("itch.io", "https://armaisdiaz.itch.io/"),
]


# ---- Utilidades

def esc(texto):
    return html.escape(texto, quote=True)


def formato(texto):
    """Escapa el texto y convierte **negrita** en <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(texto))


def sin_formato(texto):
    return texto.replace("**", "")


def rel(desde, hasta):
    """Enlace relativo de la pagina del directorio `desde` al directorio o fichero `hasta` (rutas desde la raiz)."""
    if hasta == "" or hasta.endswith("/"):
        r = posixpath.relpath("/" + hasta, "/" + desde)
        return "./" if r == "." else r + "/"
    return posixpath.relpath("/" + hasta, "/" + desde)


def fecha_larga(fecha, idioma):
    d = datetime.date.fromisoformat(fecha)
    mes = TXT[idioma]["meses"][d.month - 1]
    return f"{d.day} de {mes} de {d.year}" if idioma == "es" else f"{mes} {d.day}, {d.year}"


def slug(e):
    return f"{e['juego']}-{e['version'].replace('.', '-')}"


def url_entrada(e, idioma):
    return TXT[idioma]["lista"] + slug(e) + "/"


# ---- Entradas

def cargar():
    entradas, errores = [], []
    for f in sorted(ENTRADAS.glob("*.json")):
        try:
            e = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            errores.append(f"{f.name}: no es JSON valido ({err})")
            continue
        def mal(msg):
            errores.append(f"{f.name}: {msg}")
        if e.get("juego") not in JUEGOS:
            mal(f"«juego» tiene que ser uno de {', '.join(JUEGOS)}")
            continue
        if not re.fullmatch(r"\d+(\.\d+)*", str(e.get("version", ""))):
            mal("«version» tiene que ser como 1.3.0")
            continue
        try:
            datetime.date.fromisoformat(e.get("fecha", ""))
        except ValueError:
            mal("«fecha» tiene que ser AAAA-MM-DD")
            continue
        if f.name != f"{e['juego']}-{e['version']}.json":
            mal(f"el fichero tiene que llamarse {e['juego']}-{e['version']}.json")
        if e.get("prueba_cerrada") and not JUEGOS[e["juego"]]["prueba"]:
            mal("«prueba_cerrada», pero ese juego no tiene enlace de prueba en JUEGOS")
        for idioma in ("es", "en"):
            t = e.get(idioma) or {}
            if not t.get("titulo") or not isinstance(t.get("cambios"), list) or not t["cambios"]:
                mal(f"«{idioma}» necesita «titulo» y una lista «cambios» no vacia")
            elif any(not isinstance(c, str) or not c.strip() for c in t["cambios"]):
                mal(f"«{idioma}.cambios»: cada cambio es un texto no vacio")
        entradas.append(e)
    vistos = {}
    for e in entradas:
        if slug(e) in vistos:
            errores.append(f"{e['juego']} {e['version']} esta dos veces")
        vistos[slug(e)] = e
    if errores:
        sys.exit("Novedades con errores:\n  " + "\n  ".join(errores))
    # De la mas nueva a la mas vieja; el mismo dia, por juego
    return sorted(entradas, key=lambda e: (e["fecha"], e["juego"]), reverse=True)


# ---- Lo que se copia de la portada

def de_la_portada():
    portada = (RAIZ / "index.html").read_text(encoding="utf-8")
    css = re.search(r"css/site\.css\?v=([0-9a-z]+)", portada).group(1)
    js = re.search(r"js/sitio\.js\?v=([0-9a-z]+)", portada).group(1)
    ano = re.search(r"© (\d{4}) Astro Arcade", portada).group(1)
    return css, js, ano


# ---- Piezas de las paginas

def tarjeta(e, idioma, desde, nivel):
    t = TXT[idioma]
    juego = JUEGOS[e["juego"]]
    return f"""        <li class="novedad">
          <a href="{rel(desde, url_entrada(e, idioma))}">
            <img src="{rel(desde, f"img/juegos/{e['juego']}.webp")}" alt="" width="1024" height="500" loading="lazy">
            <div>
              <p class="novedad-meta"><strong>{esc(juego['nombre'])} {esc(e['version'])}</strong> · <time datetime="{e['fecha']}">{fecha_larga(e['fecha'], idioma)}</time></p>
              <h{nivel} class="novedad-titulo">{esc(e[idioma]['titulo'])}</h{nivel}>
            </div>
          </a>
        </li>"""


def pagina(idioma, ruta, titulo, descripcion, og_titulo, og_imagen, og_tipo, ruta_otra, cuerpo, versiones,
           actual_lista=False, ld=None, marca_play=False):
    t, o = TXT[idioma], TXT[TXT[idioma]["otro_lang"]]
    css, js, ano = versiones
    r = lambda hasta: rel(ruta, hasta)
    canon_es = WEB + (ruta if idioma == "es" else ruta_otra)
    canon_en = WEB + (ruta if idioma == "en" else ruta_otra)
    actual = ' aria-current="page"' if actual_lista else ""
    ld_html = ""
    if ld:
        ld_html = ('\n  <script type="application/ld+json">\n  '
                   + json.dumps(ld, ensure_ascii=False, indent=2).replace("\n", "\n  ") + "\n  </script>\n")
    redes = "\n".join(f'      <li><a href="{u}">{n}</a></li>' for n, u in REDES)
    return f"""<!DOCTYPE html>
<html lang="{t['lang']}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(titulo)}</title>
  <meta name="description" content="{esc(descripcion)}">
  <link rel="canonical" href="{WEB}{ruta}">
  <link rel="alternate" hreflang="es" href="{canon_es}">
  <link rel="alternate" hreflang="en" href="{canon_en}">
  <link rel="alternate" hreflang="x-default" href="{canon_es}">
  <meta name="theme-color" content="#121626">

  <link rel="icon" href="{r('favicon.ico')}" sizes="16x16 32x32 48x48">
  <link rel="apple-touch-icon" href="{r('apple-touch-icon.png')}">

  <meta property="og:type" content="{og_tipo}">
  <meta property="og:url" content="{WEB}{ruta}">
  <meta property="og:title" content="{esc(og_titulo)}">
  <meta property="og:description" content="{esc(descripcion)}">
  <meta property="og:image" content="{WEB}{og_imagen}">
  <meta property="og:locale" content="{t['locale']}">
  <meta name="twitter:card" content="summary_large_image">
{ld_html}
  <link rel="preload" href="{r('fonts/exo2.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{r('css/site.css')}?v={css}">
  <script src="{r('js/sitio.js')}?v={js}" defer></script>
</head>
<body>
  <!-- Generada por tools/novedades/generar.py: no se edita a mano -->
  <nav class="barra barra-siempre" aria-label="{t['menu']}">
    <a class="barra-marca" href="{r(t['inicio'])}"><img src="{r('apple-touch-icon.png')}" alt="" width="180" height="180"><span>Astro Arcade</span></a>
    <div class="barra-menu" id="menu" popover>
      <a href="{r(t['inicio'])}{t['ancla_juegos']}">{t['juegos']}</a>
      <a class="opcional" href="{r(t['lista'])}"{actual}>{t['novedades']}</a>
      <a class="opcional" href="{r(t['inicio'])}{t['ancla_nosotros']}">{t['nosotros']}</a>
      <a class="opcional" href="{r(t['prensa'])}">{t['prensa_txt']}</a>
      <a class="opcional" href="{r(t['inicio'])}{t['ancla_contacto']}">{t['contacto']}</a>
    </div>
    <a class="barra-idioma" href="{r(ruta_otra)}" hreflang="{o['lang']}" lang="{o['lang']}" aria-label="{t['otro_idioma_nombre']}">{t['otro_idioma']}</a>
    <a class="boton" href="{r(JUEGOS['orbit-rivals'][idioma]['jugar'])}">{t['jugar']}</a>
    <button class="barra-abrir" type="button" popovertarget="menu" aria-label="{t['menu']}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16"/><path d="M4 12h16"/><path d="M4 17h16"/></svg></button>
  </nav>

  <main>
{cuerpo}
  </main>

  <footer class="pie">
    <ul class="pie-menu">
      <li><a href="{r(t['inicio'])}{t['ancla_juegos']}">{t['juegos']}</a></li>
      <li><a href="{r(t['lista'])}">{t['novedades']}</a></li>
      <li><a href="{r(t['prensa'])}">{t['prensa_txt']}</a></li>
      <li><a href="{r(t['privacidad'])}">{t['privacidad_txt']}</a></li>
{redes}
      <li><a href="{r(ruta_otra)}" hreflang="{o['lang']}" lang="{o['lang']}">{t['otro_idioma_nombre']}</a></li>
    </ul>
    <p>© {ano} Astro Arcade{'.' + t['marca_play'] if marca_play else ''}</p>
  </footer>
</body>
</html>
"""


def pagina_lista(entradas, idioma, versiones):
    t = TXT[idioma]
    ruta = t["lista"]
    tarjetas = "\n".join(tarjeta(e, idioma, ruta, 2) for e in entradas)
    cuerpo = f"""    <section class="seccion seccion-pegada" aria-labelledby="titulo-novedades">
      <h1 id="titulo-novedades" class="titular"><span>{t['titulo_lista']}</span></h1>
      <p class="entradilla">{t['entradilla']}</p>
      <ul class="novedades">
{tarjetas}
      </ul>
    </section>"""
    return pagina(idioma, ruta, f"{t['titulo_lista']} | Astro Arcade", t["desc_lista"],
                  f"{t['titulo_lista']} · Astro Arcade", "img/compartir.jpg", "website",
                  TXT[t["otro_lang"]]["lista"], cuerpo, versiones, actual_lista=True)


def pagina_entrada(e, idioma, versiones):
    t = TXT[idioma]
    juego = JUEGOS[e["juego"]]
    ruta = url_entrada(e, idioma)
    r = lambda hasta: rel(ruta, hasta)
    titulo = e[idioma]["titulo"]
    nombre = f"{juego['nombre']} {e['version']}"
    cambios = "\n".join(f"        <li>{formato(c)}</li>" for c in e[idioma]["cambios"])

    prueba = ""
    if e.get("prueba_cerrada"):
        pasos = "\n".join("          <li>" + p.format(grupo=GRUPO_TESTERS, prueba=juego["prueba"]) + "</li>"
                          for p in t["prueba_pasos"])
        prueba = f"""
      <section class="novedad-prueba" aria-labelledby="titulo-prueba">
        <h2 id="titulo-prueba">{t['prueba_titulo']}</h2>
        <p>{esc(t['prueba_intro'].format(juego=juego['nombre']))}</p>
        <ol>
{pasos}
        </ol>
        <p>{t['prueba_final']}</p>
      </section>
"""

    play = ""
    if juego["google_play"]:
        enlace = (f"{juego['google_play']}&amp;utm_source=astroarcade&amp;utm_medium=web"
                  f"&amp;utm_campaign={t['play_campana']}")
        play = (f'\n        <a class="insignia-play" href="{enlace}"><img src="{r(t["play_img"])}" '
                f'alt="{t["play_alt"]}" width="646" height="250" loading="lazy"></a>')

    cuerpo = f"""    <article class="seccion seccion-pegada novedad-pagina" aria-labelledby="titulo-entrada">
      <p class="novedad-volver"><a href="{r(t['lista'])}">{t['volver']}</a></p>
      <div class="novedad-cabecera">
        <img src="{r(f"img/juegos/{e['juego']}.webp")}" alt="" width="1024" height="500">
        <div>
          <p class="juego-genero"><a href="{r(juego[idioma]['pagina'])}">{esc(juego['nombre'])}</a> {esc(e['version'])} · <time datetime="{e['fecha']}">{fecha_larga(e['fecha'], idioma)}</time></p>
          <h1 id="titulo-entrada" class="titular"><span>{esc(titulo)}</span></h1>
        </div>
      </div>
      <ul class="novedad-cambios">
{cambios}
      </ul>
{prueba}
      <div class="botones">
        <a class="boton" href="{r(juego[idioma]['jugar'])}">{t['jugar_gratis']}</a>{play}
        <a class="boton boton-secundario" href="{r(juego[idioma]['pagina'])}">{t['detalles']}</a>
      </div>
    </article>"""

    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": f"{nombre}: {titulo}",
        "datePublished": e["fecha"],
        "inLanguage": idioma,
        "url": WEB + ruta,
        "image": f"{WEB}img/juegos/{e['juego']}.jpg",
        "author": {"@type": "Organization", "name": "Astro Arcade", "url": WEB},
        "publisher": {"@type": "Organization", "name": "Astro Arcade",
                      "logo": {"@type": "ImageObject", "url": WEB + "apple-touch-icon.png"}},
        "about": {"@type": "VideoGame", "name": juego["nombre"], "url": WEB + juego[idioma]["pagina"]},
    }
    return pagina(idioma, ruta, f"{nombre}: {titulo} | Astro Arcade",
                  t["desc_entrada"].format(juego=juego["nombre"], version=e["version"], titulo=titulo),
                  f"{nombre}: {titulo}", f"img/juegos/{e['juego']}.jpg", "article",
                  url_entrada(e, t["otro_lang"]), cuerpo, versiones, ld=ld, marca_play=bool(play))


def bloque_portada(entradas, idioma):
    t = TXT[idioma]
    desde = t["inicio"]
    seccion = "novedades" if idioma == "es" else "news"
    tarjetas = "\n".join(tarjeta(e, idioma, desde, 3) for e in entradas[:EN_PORTADA])
    return f"""<!-- novedades:inicio -->
    <!-- Las tres ultimas novedades: las pone tools/novedades/generar.py, no se editan a mano -->
    <section id="{seccion}" class="seccion" aria-labelledby="titulo-{seccion}">
      <h2 id="titulo-{seccion}" class="titular"><span>{t['titulo_lista']}</span></h2>
      <p class="entradilla">{t['entradilla']}</p>
      <ul class="novedades">
{tarjetas}
      </ul>
      <div class="botones">
        <a class="boton boton-secundario" href="{rel(desde, t['lista'])}">{t['ver_todas']}</a>
      </div>
    </section>
    <!-- novedades:fin -->"""


# ---- El sitemap

def sitemap(texto, entradas):
    nueva = entradas[0]["fecha"] if entradas else None
    lineas = [l for l in texto.splitlines()
              if not re.search(r"<loc>https://astroarcade\.es/(novedades|en/news)/", l)]
    # La portada cambia cuando entra una novedad
    def portada(m):
        return f"<loc>{m.group(1)}</loc><lastmod>{max(m.group(2), nueva) if nueva else m.group(2)}</lastmod>"
    lineas = [re.sub(r"<loc>(https://astroarcade\.es/(?:en/)?)</loc><lastmod>([^<]+)</lastmod>", portada, l)
              for l in lineas]
    nuevas = []
    if entradas:
        for idioma in ("es", "en"):
            nuevas.append((WEB + TXT[idioma]["lista"], nueva))
            nuevas += [(WEB + url_entrada(e, idioma), e["fecha"]) for e in entradas]
    fin = lineas.index("</urlset>")
    lineas[fin:fin] = [f"  <url><loc>{u}</loc><lastmod>{f}</lastmod></url>" for u, f in sorted(nuevas)]
    return "\n".join(lineas) + "\n"


# ---- Todo junto

def generar():
    """Devuelve {ruta: contenido} de todo lo que tiene que haber, y las carpetas de novedades que sobran."""
    entradas = cargar()
    versiones = de_la_portada()
    ficheros = {}
    for idioma in ("es", "en"):
        lista = TXT[idioma]["lista"]
        ficheros[lista + "index.html"] = pagina_lista(entradas, idioma, versiones)
        for e in entradas:
            ficheros[url_entrada(e, idioma) + "index.html"] = pagina_entrada(e, idioma, versiones)
        portada = TXT[idioma]["inicio"] + "index.html"
        texto = (RAIZ / portada).read_text(encoding="utf-8")
        patron = re.compile(r"<!-- novedades:inicio -->.*?<!-- novedades:fin -->", re.S)
        if not patron.search(texto):
            sys.exit(f"{portada} no tiene las marcas <!-- novedades:inicio --> y <!-- novedades:fin -->")
        ficheros[portada] = patron.sub(lambda m: bloque_portada(entradas, idioma), texto, count=1)
    ficheros["sitemap.xml"] = sitemap((RAIZ / "sitemap.xml").read_text(encoding="utf-8"), entradas)

    sobran = []
    for idioma in ("es", "en"):
        carpeta = RAIZ / TXT[idioma]["lista"]
        if carpeta.is_dir():
            validas = {slug(e) for e in entradas}
            sobran += [d for d in carpeta.iterdir() if d.is_dir() and d.name not in validas]
    return ficheros, sobran


def main():
    comprobar = "--comprobar" in sys.argv[1:]
    ficheros, sobran = generar()
    distintos = [ruta for ruta, contenido in ficheros.items()
                 if not (RAIZ / ruta).exists() or (RAIZ / ruta).read_text(encoding="utf-8") != contenido]
    if comprobar:
        if distintos or sobran:
            print("Novedades sin generar:", *distintos, *(str(d.relative_to(RAIZ)) for d in sobran), sep="\n  ")
            sys.exit(1)
        print("Novedades al día.")
        return
    for ruta in distintos:
        destino = RAIZ / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(ficheros[ruta], encoding="utf-8")
        print("escrito", ruta)
    for d in sobran:
        shutil.rmtree(d)
        print("borrado", d.relative_to(RAIZ))
    if not distintos and not sobran:
        print("Novedades al día: no había nada que cambiar.")


if __name__ == "__main__":
    main()
