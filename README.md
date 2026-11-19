# Maquinarias Agrícolas Nuevo Campo

Sitio de maquinaria agrícola de mediano y gran tamaño (Pichidegua, Región de O'Higgins).
Construido sobre la base del proyecto de clase "Panadería La Espiga" (Django).
La interfaz usa Bootstrap 5.3.3 desde jsDelivr y conserva estilos propios para la identidad visual del sitio.
Los productos, horarios y datos de la empresa se administran en `datos.json`, en la raíz del repositorio.

## Secciones

- Inicio
- Quiénes Somos
- Productos (tractores, cosechadoras, labranza, transporte y forraje)
- Contacto
- Ubicación (Pichidegua, O'Higgins, con mapa)
- Horarios

## Funciones del sitio

- **Fotos reales de maquinaria.** Cada producto del JSON puede declarar un campo
  `foto` con la ruta dentro de `static/`. Si no lo tiene, la tarjeta usa la
  ilustración vectorial de `paginas/static/paginas/productos.svg`. Los créditos y
  licencias de las fotografías están en [`CREDITS.md`](CREDITS.md).
- **Cotización por producto.** El botón "Cotizar este producto" abre
  `/contacto/?producto=<nombre>` y deja el mensaje del formulario precargado.
- **Catálogo en JSON.** Todo el contenido (empresa, productos y horarios) vive en
  [`datos.json`](datos.json), en la raíz del repositorio. Desde GitHub se puede ver
  o descargar con el botón *Raw / Download*. El sitio no expone enlaces de descarga.
- **Contacto directo.** El teléfono usa `tel:` y el WhatsApp usa
  `https://wa.me/...`, así que funciona tanto en escritorio como en celular.

### Cómo agregar o cambiar un producto

1. Edita `datos.json` (raíz del repositorio) y agrega el objeto dentro de `productos`.
2. Copia la foto a `paginas/static/paginas/productos/` y escribe su ruta en
   `"foto": "paginas/productos/mi-foto.jpg"`. Usa JPEG de 1200 x 800 px o similar.
3. Agrega el crédito de la imagen en `CREDITS.md`.
4. Ejecuta `python manage.py test` para confirmar que la foto existe y se renderiza.

## Cómo correrlo (Windows)

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver

Después abrir http://127.0.0.1:8000/

## Pruebas

    python manage.py check
    python manage.py test

El formulario envía las consultas a `CONTACT_EMAIL` o, si no se define, a la
dirección de ventas configurada en `datos.json`. En desarrollo,
Django usa el backend de consola y muestra el correo en la terminal del servidor;
no envía correo real.

## Configuración para publicar

Configura estas variables en el hosting como secretos, nunca dentro del
repositorio:

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY`: clave larga, aleatoria y privada.
- `DJANGO_ALLOWED_HOSTS`: dominios permitidos separados por comas.
- `CONTACT_EMAIL`: dirección que recibirá las consultas (opcional; por defecto
  se usa el correo de ventas del JSON).
- `DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` y
  `EMAIL_USE_TLS` según el proveedor SMTP.
- `DEFAULT_FROM_EMAIL`: remitente aceptado por el proveedor de correo.
- `DJANGO_SECURE_SSL_REDIRECT=True` y `DJANGO_SECURE_HSTS_SECONDS` una vez que
  HTTPS funcione correctamente en el hosting.

Al desactivar `DJANGO_DEBUG`, la aplicación exige una clave secreta y dominios
permitidos; al seleccionar SMTP, también exige `EMAIL_HOST`. `runserver` es solo
para desarrollo: publica con el servidor WSGI/ASGI recomendado por el proveedor.
