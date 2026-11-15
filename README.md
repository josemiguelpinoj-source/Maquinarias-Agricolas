# Maquinarias Agrícolas Nuevo Campo

Sitio de maquinaria agrícola de mediano y gran tamaño (Pichidegua, Región de O'Higgins).
Construido sobre la base del proyecto de clase "Panadería La Espiga" (Django).
La interfaz usa Bootstrap 5.3.3 desde jsDelivr y conserva estilos propios para la identidad visual del sitio.
Los productos, horarios y datos de la empresa se administran en `paginas/data/contenido.json`.

## Secciones

- Inicio
- Quiénes Somos
- Productos (tractores, cosechadoras, labranza, transporte)
- Contacto
- Ubicación (Pichidegua, O'Higgins, con mapa)
- Horarios

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
dirección de ventas configurada en `paginas/data/contenido.json`. En desarrollo,
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
