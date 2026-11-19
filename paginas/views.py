import json
import logging
from pathlib import Path
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ConsultaContactoForm


DATA_FILE = Path(settings.BASE_DIR) / "datos.json"
logger = logging.getLogger(__name__)


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
    site_data = _load_site_data()
    producto_consulta = request.GET.get("producto", "").strip()[:160]
    initial = {}
    if producto_consulta:
        initial["mensaje"] = f"Hola, quiero cotizar: {producto_consulta}."
    form = ConsultaContactoForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        datos = form.cleaned_data
        empresa = site_data["empresa"]
        recipient = settings.CONTACT_EMAIL or empresa["correo_ventas"]
        email = EmailMessage(
            subject="Nueva consulta desde el sitio web de Nuevo Campo",
            body=(
                f"Nombre: {datos['nombre']}\n"
                f"Correo: {datos['correo']}\n"
                f"Teléfono: {datos['telefono'] or 'No indicado'}\n\n"
                f"Consulta:\n{datos['mensaje']}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[datos["correo"]],
        )
        try:
            sent = email.send(fail_silently=False)
        except (OSError, SMTPException):
            logger.exception("No se pudo enviar una consulta de contacto")
            messages.error(
                request,
                f"No pudimos enviar tu consulta. Inténtalo más tarde o llámanos al {empresa['whatsapp']}.",
            )
        else:
            if sent != 1:
                logger.error("El backend de correo no envió la consulta de contacto")
                messages.error(
                    request,
                    f"No pudimos enviar tu consulta. Inténtalo más tarde o llámanos al {empresa['whatsapp']}.",
                )
            else:
                messages.success(
                    request,
                    "¡Gracias por escribirnos! Recibimos tu consulta y te responderemos a la brevedad.",
                )
                return redirect("contacto")

    contexto = {"form": form}
    if producto_consulta:
        contexto["producto_consulta"] = producto_consulta
    return _render_page(request, "paginas/contacto.html", contexto, site_data)


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
