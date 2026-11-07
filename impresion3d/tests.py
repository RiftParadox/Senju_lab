from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Encargo, EstadoEncargo, EstadoSolicitud, SolicitudPedido


class SolicitudEncargoFlowTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.customer = user_model.objects.create_user(username="cliente", password="test-pass")
		self.admin = user_model.objects.create_user(username="taller", password="test-pass", is_staff=True)
		self.customer_api = APIClient()
		self.customer_api.force_authenticate(self.customer)
		self.admin_api = APIClient()
		self.admin_api.force_authenticate(self.admin)

	def test_customer_acceptance_creates_one_agendado_order(self):
		request = SolicitudPedido.objects.create(
			user=self.customer,
			descripcion="Soporte de sensor",
			estado=EstadoSolicitud.COTIZADA,
			precio_cotizado="120.00",
		)

		response = self.customer_api.patch(
			reverse("solicitudpedido-detail", args=[request.pk]),
			{"estado": EstadoSolicitud.ACEPTADA},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		order = Encargo.objects.get(solicitud=request)
		self.assertEqual(order.estado, EstadoEncargo.AGENDADO)

	def test_admin_can_create_order_only_for_accepted_request(self):
		pending_request = SolicitudPedido.objects.create(
			user=self.customer,
			descripcion="Pieza pendiente",
			estado=EstadoSolicitud.PENDIENTE,
		)
		pending_response = self.admin_api.post(
			reverse("encargo-list"),
			{"solicitud": pending_request.pk, "nombre_modelo": "Modelo pendiente", "escala": "1:1"},
			format="json",
		)
		self.assertEqual(pending_response.status_code, status.HTTP_400_BAD_REQUEST)

		accepted_request = SolicitudPedido.objects.create(
			user=self.customer,
			descripcion="Pieza aceptada",
			estado=EstadoSolicitud.ACEPTADA,
		)
		create_response = self.admin_api.post(
			reverse("encargo-list"),
			{"solicitud": accepted_request.pk, "nombre_modelo": "Modelo aceptado", "escala": "1:1"},
			format="json",
		)
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Encargo.objects.get(solicitud=accepted_request).estado, EstadoEncargo.AGENDADO)

		duplicate_response = self.admin_api.post(
			reverse("encargo-list"),
			{"solicitud": accepted_request.pk, "nombre_modelo": "Duplicado", "escala": "1:1"},
			format="json",
		)
		self.assertEqual(duplicate_response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_customer_cannot_create_order(self):
		accepted_request = SolicitudPedido.objects.create(
			user=self.customer,
			descripcion="Solicitud aceptada",
			estado=EstadoSolicitud.ACEPTADA,
		)

		response = self.customer_api.post(
			reverse("encargo-list"),
			{"solicitud": accepted_request.pk, "nombre_modelo": "Modelo", "escala": "1:1"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
