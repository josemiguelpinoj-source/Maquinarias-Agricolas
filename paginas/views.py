import json
from pathlib import Path

from django.shortcuts import render


DATA_FILE = Path(__file__).resolve().parent / "data" / "contenido.json"


def _load_site_data():
    with DATA_FILE.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def _render_page(request, template_name, context=None, site_data=None):
    if site_data is None:
        site_data = _load_site_data()

    page_context = {"empresa": site_data["empresa"]}
    if context is not None:
        page_context.update(context)
    return render(request, template_name, page_context)


def inicio(request):
    site_data = _load_site_data()
    destacados = [
        producto for producto in site_data["productos"]
        if producto["destacado"]
    ]
    return _render_page(
        request,
        "paginas/inicio.html",
        {"productos_destacados": destacados},
        site_data,
    )


def productos(request):
    site_data = _load_site_data()
    return _render_page(
        request,
        "paginas/productos.html",
        {"productos": site_data["productos"]},
        site_data,
    )


def nosotros(request):
    return _render_page(request, "paginas/nosotros.html")


def horarios(request):
    site_data = _load_site_data()
    return _render_page(
        request,
        "paginas/horarios.html",
        {"horarios": site_data["horarios"]},
        site_data,
    )


def contacto(request):
    mensaje = None
    if request.method == "POST":
        mensaje = "¡Gracias por escribirnos! Recibimos tu consulta y te responderemos a la brevedad."
    return _render_page(request, "paginas/contacto.html", {"mensaje": mensaje})


def ubicacion(request):
    site_data = _load_site_data()
    empresa = site_data["empresa"]
    latitud = empresa["latitud"]
    longitud = empresa["longitud"]
    contexto = {
        "direccion": empresa["direccion"],
        "latitud": latitud,
        "longitud": longitud,
        "mapa_embed": (
            "https://www.openstreetmap.org/export/embed.html"
            f"?bbox={empresa['mapa_bbox']}&layer=mapnik&marker={latitud}%2C{longitud}"
        ),
        "enlace_mapa": f"https://www.openstreetmap.org/?mlat={latitud}&mlon={longitud}#map=13/{latitud}/{longitud}",
    }
    return _render_page(request, "paginas/ubicacion.html", contexto, site_data)
