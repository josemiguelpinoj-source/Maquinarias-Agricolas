import json
from pathlib import Path

from django.test import TestCase


class BootstrapLayoutTests(TestCase):
    def test_shared_layout_loads_bootstrap_and_has_responsive_navigation(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "bootstrap@5.3.3/dist/css/bootstrap.min.css")
        self.assertContains(response, 'data-bs-target="#navegacionPrincipal"')
        self.assertContains(response, 'class="site-main container flex-grow-1')

    def test_pages_render_with_the_shared_bootstrap_layout(self):
        for path in ("nosotros/", "productos/", "contacto/", "ubicacion/", "horarios/"):
            with self.subTest(path=path):
                response = self.client.get(f"/{path}")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "bootstrap@5.3.3/dist/css/bootstrap.min.css")

    def test_contact_form_uses_bootstrap_form_controls(self):
        response = self.client.get("/contacto/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="form-control"')
        self.assertContains(response, 'class="btn boton w-100"')


class JsonContentTests(TestCase):
    def setUp(self):
        data_file = Path(__file__).resolve().parent / "data" / "contenido.json"
        with data_file.open(encoding="utf-8") as file:
            self.site_data = json.load(file)

    def test_product_catalog_and_homepage_use_json_products(self):
        catalog = self.client.get("/productos/")
        homepage = self.client.get("/")
        featured = [
            product for product in self.site_data["productos"]
            if product["destacado"]
        ]

        self.assertEqual(catalog.context["productos"], self.site_data["productos"])
        self.assertEqual(homepage.context["productos_destacados"], featured)
        self.assertContains(catalog, "#tractor")
        self.assertContains(catalog, "#cosechadora")

    def test_hours_location_and_company_contact_details_come_from_json(self):
        hours_page = self.client.get("/horarios/")
        contact_page = self.client.get("/contacto/")
        location_page = self.client.get("/ubicacion/")

        self.assertEqual(hours_page.context["horarios"], self.site_data["horarios"])
        self.assertContains(contact_page, self.site_data["empresa"]["correo_ventas"])
        self.assertContains(contact_page, self.site_data["empresa"]["telefono_fijo"])
        self.assertEqual(
            location_page.context["direccion"],
            self.site_data["empresa"]["direccion"],
        )
