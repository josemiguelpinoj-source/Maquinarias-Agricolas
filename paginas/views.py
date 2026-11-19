import json
import logging
from datetime import time, timedelta
from pathlib import Path
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import ConsultaContactoForm


DATA_FILE = Path(settings.BASE_DIR) / "datos.json"
DIAS_SEMANA = (
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
)
MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)
logger = logging.getLogger(__name__)


def _load_site_data():
    with DATA_FILE.open(encoding="utf-8") as data_file:
        return json.load(data_file)


def _ahora_local():
    return timezone.localtime()


def _hora_del_dia(valor):
    if not valor:
        return None
    horas, minutos = valor.split(":")
    return time(int(horas), int(minutos))


def _grupo_horario(horarios, fecha):
    nombre_dia = DIAS_SEMANA[fecha.weekday()]
    for grupo in horarios:
        if nombre_dia in grupo.get("dias", []):
            return grupo
    return None


def _proxima_apertura(horarios, ahora):
    for salto in range(8):
        fecha = ahora.date() + timedelta(days=salto)
        grupo = _grupo_horario(horarios, fecha)
        if grupo is None:
            continue
        apertura = _hora_del_dia(grupo.get("apertura"))
        if apertura is None:
            continue
        if salto == 0 and ahora.time() >= apertura:
            continue
        return fecha, apertura, salto
    return None, None, None


def _estado_horarios(horarios, ahora):
    grupo_hoy = _grupo_horario(horarios, ahora.date())
    apertura_hoy = _hora_del_dia(grupo_hoy.get("apertura")) if grupo_hoy else None
    cierre_hoy = _hora_del_dia(grupo_hoy.get("cierre")) if grupo_hoy else None
    abierto_ahora = bool(
        apertura_hoy
        and cierre_hoy
        and apertura_hoy <= ahora.time() < cierre_hoy
    )

    filas = []
    for grupo in horarios:
        es_hoy = grupo is grupo_hoy
        if es_hoy:
            abierto = abierto_ahora
            estado = "Abierto" if abierto else "Cerrado"
        else:
            abierto = False
            estado = "Cerrado"
        filas.append({
            **grupo,
            "es_hoy": es_hoy,
            "abierto": abierto,
            "estado": estado,
        })

    if abierto_ahora:
        detalle = f"Cerramos a las {cierre_hoy:%H:%M}."
    else:
        _, apertura, salto = _proxima_apertura(horarios, ahora)
        if apertura is None:
            detalle = "Consulta nuestros horarios de atención."
        elif salto == 0:
            detalle = f"Abrimos hoy a las {apertura:%H:%M}."
        elif salto == 1:
            detalle = f"Abrimos mañana a las {apertura:%H:%M}."
        else:
            proximo_dia = ahora.date() + timedelta(days=salto)
            detalle = (
                f"Abrimos el {DIAS_SEMANA[proximo_dia.weekday()]} "
                f"a las {apertura:%H:%M}."
            )

    estado_actual = {
        "abierto": abierto_ahora,
        "titulo": "Abierto" if abierto_ahora else "Cerrado",
        "detalle": detalle,
        "hora": ahora.strftime("%H:%M"),
        "dia": (
            f"{DIAS_SEMANA[ahora.weekday()]} {ahora.day} "
            f"de {MESES[ahora.month - 1]}"
        ),
    }
    return filas, estado_actual


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
    filas, estado_actual = _estado_horarios(site_data["horarios"], _ahora_local())
    return _render_page(
        request,
        "paginas/horarios.html",
        {
            "horarios": filas,
            "estado_horario": estado_actual,
            "horarios_datos": site_data["horarios"],
        },
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
