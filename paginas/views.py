from django.shortcuts import render


def inicio(request):
    return render(request, "paginas/inicio.html")


def productos(request):
    productos = [
        {
            "nombre": "Tractor 4x4 mediano 90–120 HP",
            "categoria": "Mediano",
            "linea": "Tractores",
            "descripcion": "Versátil para aradura, rastraje, siembra y transporte corto. Cabina climatizada y toma de fuerza.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Tractor 4x4 grande 130–220 HP",
            "categoria": "Grande",
            "linea": "Tractores",
            "descripcion": "Alta potencia para labores intensivas, grandes implementos y trabajo en terrenos exigentes.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Cosechadora de granos 14–20 pies",
            "categoria": "Grande",
            "linea": "Cosecha",
            "descripcion": "Para trigo, maíz y soya, con trilla de alto rendimiento y limpia de grano ajustable.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Cosechadora de papas",
            "categoria": "Grande",
            "linea": "Cosecha",
            "descripcion": "Sistema de bandejas regulable, ideal para parcelas medianas y grandes de papa.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Pulverizadora autopropelida 24–30 m",
            "categoria": "Grande",
            "linea": "Protección de cultivos",
            "descripcion": "Brazo plegable, bomba de presión variable y depósito de gran capacidad para granjas de alto rendimiento.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Arado de discos semihorizontal",
            "categoria": "Grande",
            "linea": "Labranza",
            "descripcion": "Implemento de 7 a 13 discos para labranza primaria en suelos con residuos vegetales.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Rastra de discos",
            "categoria": "Mediano",
            "linea": "Labranza",
            "descripcion": "Para preparación de cama de siembra y mezcla de residuos. Distintos anchos de trabajo.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Subsoleador / escarificador",
            "categoria": "Grande",
            "linea": "Labranza",
            "descripcion": "Descompactación profunda sin voltear el suelo, ideal para suelos de riego de la zona.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Camión tolva agrícola",
            "categoria": "Grande",
            "linea": "Transporte",
            "descripcion": "Transporte de granos y forraje entre la parcela y el silo, con descarga hidráulica.",
            "precio": "Consultar precio",
        },
        {
            "nombre": "Prensa enroladora de fardos",
            "categoria": "Mediano",
            "linea": "Forraje",
            "descripcion": "Enrolado de alto rendimiento para pradera y forraje, con atado de alambre o red.",
            "precio": "Consultar precio",
        },
    ]
    return render(request, "paginas/productos.html", {"productos": productos})


def nosotros(request):
    return render(request, "paginas/nosotros.html")


def horarios(request):
    horarios = [
        {"dia": "Lunes a viernes", "horario": "08:00 a 18:00", "estado": "Abierto", "abierto": True},
        {"dia": "Sábado", "horario": "08:30 a 14:00", "estado": "Abierto", "abierto": True},
        {"dia": "Domingo", "horario": "Cerrado", "estado": "Cerrado", "abierto": False},
        {"dia": "Feriados nacionales", "horario": "Cerrado", "estado": "Cerrado", "abierto": False},
    ]
    return render(request, "paginas/horarios.html", {"horarios": horarios})


def contacto(request):
    mensaje = None
    if request.method == "POST":
        mensaje = "¡Gracias por escribirnos! Recibimos tu consulta y te responderemos a la brevedad."
    return render(request, "paginas/contacto.html", {"mensaje": mensaje})


def ubicacion(request):
    latitud = "-34.3536"
    longitud = "-71.3361"
    bbox = "-71.4100,-34.3950,-71.2850,-34.3150"
    contexto = {
        "direccion": "Camino a Pichidegua s/n, Pichidegua, Región de O'Higgins",
        "latitud": latitud,
        "longitud": longitud,
        "mapa_embed": (
            "https://www.openstreetmap.org/export/embed.html"
            f"?bbox={bbox}&layer=mapnik&marker={latitud}%2C{longitud}"
        ),
        "enlace_mapa": f"https://www.openstreetmap.org/?mlat={latitud}&mlon={longitud}#map=13/{latitud}/{longitud}",
    }
    return render(request, "paginas/ubicacion.html", contexto)
