import json
from datetime import datetime
from pathlib import Path
from smtplib import SMTPException
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings


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

    def test_photo_credits_are_not_visible_on_the_site(self):
        response = self.client.get("/nosotros/")
        content = response.content.decode()

        self.assertNotIn("Créditos de las fotografías", content)
        self.assertNotIn("creditos-fotos", content)
        self.assertNotIn("Créditos de imágenes", content)

    def test_about_page_uses_modern_tractor_photo(self):
        response = self.client.get("/nosotros/")

        self.assertContains(
            response,
            'src="/static/paginas/productos/tractor-grande.jpg"',
        )


class JsonContentTests(TestCase):
    def setUp(self):
        data_file = Path(settings.BASE_DIR) / "datos.json"
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

    def test_product_photos_exist_and_render(self):
        response = self.client.get("/productos/")
        content = response.content.decode()
        static_root = Path(settings.BASE_DIR) / "paginas" / "static"

        for product in self.site_data["productos"]:
            with self.subTest(product=product["nombre"]):
                photo = product.get("foto")
                if photo:
                    self.assertIn(f'src="/static/{photo}"', content)
                    self.assertTrue((static_root / photo).is_file())
                else:
                    self.assertIn(f'#{product["imagen"]}', content)

    def test_hours_location_and_company_contact_details_come_from_json(self):
        hours_page = self.client.get("/horarios/")
        contact_page = self.client.get("/contacto/")
        location_page = self.client.get("/ubicacion/")

        self.assertEqual(
            [(item["dia"], item["horario"]) for item in hours_page.context["horarios"]],
            [(item["dia"], item["horario"]) for item in self.site_data["horarios"]],
        )
        self.assertContains(contact_page, self.site_data["empresa"]["correo_ventas"])
        self.assertContains(contact_page, self.site_data["empresa"]["telefono_fijo"])
        self.assertEqual(
            location_page.context["direccion"],
            self.site_data["empresa"]["direccion"],
        )


class ScheduleStatusTests(TestCase):
    def setUp(self):
        data_file = Path(settings.BASE_DIR) / "datos.json"
        with data_file.open(encoding="utf-8") as file:
            self.site_data = json.load(file)

    def test_real_schedule_is_stored_with_opening_and_closing_times(self):
        lunes_a_viernes, sabado, domingo, feriados = self.site_data["horarios"]

        self.assertEqual(lunes_a_viernes["apertura"], "08:00")
        self.assertEqual(lunes_a_viernes["cierre"], "18:00")
        self.assertEqual(
            lunes_a_viernes["dias"],
            ["lunes", "martes", "miércoles", "jueves", "viernes"],
        )
        self.assertEqual(sabado["apertura"], "08:30")
        self.assertEqual(sabado["cierre"], "14:00")
        self.assertEqual(sabado["dias"], ["sábado"])
        self.assertIsNone(domingo["apertura"])
        self.assertEqual(feriados["dias"], [])

    @patch("paginas.views._ahora_local")
    def test_weekday_noon_marks_today_as_open(self, ahora_local):
        ahora_local.return_value = datetime(
            2026, 11, 19, 12, 0, tzinfo=ZoneInfo("America/Santiago")
        )
        response = self.client.get("/horarios/")
        estado = response.context["estado_horario"]
        filas = response.context["horarios"]

        self.assertTrue(estado["abierto"])
        self.assertEqual(estado["titulo"], "Abierto")
        self.assertEqual(estado["detalle"], "Cerramos a las 18:00.")
        self.assertEqual(estado["dia"], "jueves 19 de noviembre")
        self.assertTrue(filas[0]["es_hoy"])
        self.assertEqual(filas[0]["estado"], "Abierto")
        self.assertFalse(filas[1]["es_hoy"])
        self.assertEqual(filas[1]["estado"], "Cerrado")
        self.assertContains(response, ">Abierto<")
        self.assertContains(response, "etiqueta-hoy")

    @patch("paginas.views._ahora_local")
    def test_weekday_evening_shows_closed_and_next_opening(self, ahora_local):
        ahora_local.return_value = datetime(
            2026, 11, 19, 20, 22, tzinfo=ZoneInfo("America/Santiago")
        )
        response = self.client.get("/horarios/")
        estado = response.context["estado_horario"]

        self.assertFalse(estado["abierto"])
        self.assertEqual(estado["titulo"], "Cerrado")
        self.assertEqual(estado["detalle"], "Abrimos mañana a las 08:00.")
        self.assertEqual(response.context["horarios"][0]["estado"], "Cerrado")
        self.assertEqual(response.context["horarios"][1]["estado"], "Cerrado")

    @patch("paginas.views._ahora_local")
    def test_saturday_afternoon_and_sunday_point_to_monday(self, ahora_local):
        ahora_local.return_value = datetime(
            2026, 11, 21, 13, 0, tzinfo=ZoneInfo("America/Santiago")
        )
        sabado = self.client.get("/horarios/")

        self.assertTrue(sabado.context["estado_horario"]["abierto"])
        self.assertEqual(
            sabado.context["estado_horario"]["detalle"],
            "Cerramos a las 14:00.",
        )
        self.assertTrue(sabado.context["horarios"][1]["es_hoy"])
        self.assertEqual(sabado.context["horarios"][1]["estado"], "Abierto")
        self.assertEqual(sabado.context["horarios"][0]["estado"], "Cerrado")

        ahora_local.return_value = datetime(
            2026, 11, 22, 12, 0, tzinfo=ZoneInfo("America/Santiago")
        )
        domingo = self.client.get("/horarios/")

        self.assertFalse(domingo.context["estado_horario"]["abierto"])
        self.assertEqual(
            domingo.context["estado_horario"]["detalle"],
            "Abrimos mañana a las 08:00.",
        )
        self.assertTrue(domingo.context["horarios"][2]["es_hoy"])
        self.assertEqual(domingo.context["horarios"][2]["estado"], "Cerrado")


class PublicJsonFileTests(TestCase):
    def test_catalog_is_published_as_a_repository_file(self):
        data_file = Path(settings.BASE_DIR) / "datos.json"

        self.assertTrue(data_file.is_file())
        data = json.loads(data_file.read_text(encoding="utf-8"))
        self.assertEqual(data["empresa"]["nombre"], "Maquinarias Agrícolas Nuevo Campo")
        self.assertEqual(len(data["productos"]), 10)

    def test_site_does_not_expose_a_json_download(self):
        self.assertEqual(self.client.get("/datos.json").status_code, 404)

        home = self.client.get("/").content.decode()
        self.assertNotIn("Descargar JSON", home)


class ContactFormTests(TestCase):
    def test_product_query_prefills_the_contact_message(self):
        response = self.client.get(
            "/contacto/",
            {"producto": "Tractor 4x4 mediano 90–120 HP"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Consulta preparada para:")
        self.assertEqual(
            response.context["form"].initial["mensaje"],
            "Hola, quiero cotizar: Tractor 4x4 mediano 90–120 HP.",
        )

    @override_settings(
        MAILERS={
            "default": {
                "BACKEND": "django.core.mail.backends.locmem.EmailBackend"
            }
        }
    )
    def test_valid_contact_form_sends_email_and_redirects(self):
        response = self.client.post(
            "/contacto/",
            {
                "nombre": "Ana Pérez",
                "correo": "ana@example.cl",
                "telefono": "+56912345678",
                "mensaje": "Busco un tractor mediano.",
            },
        )

        self.assertRedirects(response, "/contacto/")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].to,
            [settings.CONTACT_EMAIL or "ventas@nuevocampo.cl"],
        )
        self.assertEqual(mail.outbox[0].reply_to, ["ana@example.cl"])
        self.assertIn("Busco un tractor mediano.", mail.outbox[0].body)

    def test_invalid_contact_form_does_not_claim_success(self):
        response = self.client.post("/contacto/", {"nombre": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Este campo es obligatorio.")
        self.assertNotContains(response, "Recibimos tu consulta")
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(
        MAILERS={
            "default": {
                "BACKEND": "django.core.mail.backends.locmem.EmailBackend"
            }
        }
    )
    @patch(
        "paginas.views.EmailMessage.send",
        side_effect=SMTPException("mail unavailable"),
    )
    def test_email_failure_is_reported_without_success(self, send_email):
        with self.assertLogs("paginas.views", level="ERROR"):
            response = self.client.post(
                "/contacto/",
                {
                    "nombre": "Ana Pérez",
                    "correo": "ana@example.cl",
                    "telefono": "",
                    "mensaje": "Busco un tractor mediano.",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No pudimos enviar tu consulta.")
        self.assertNotContains(response, "Recibimos tu consulta")
        send_email.assert_called_once()
