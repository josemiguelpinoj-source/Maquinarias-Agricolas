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
