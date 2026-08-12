from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from appointments.models import Appointment
from doctors.models import Doctor, DoctorAvailability


User = get_user_model()


class AppointmentApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="one@example.com",
            email="one@example.com",
            first_name="Patient One",
            password="SecureClinic@123",
        )
        self.other_user = User.objects.create_user(
            username="two@example.com",
            email="two@example.com",
            first_name="Patient Two",
            password="SecureClinic@123",
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Test",
            specialty="General Medicine",
            qualification="MBBS",
            experience=10,
            rating=4.8,
            consultation_fee=150,
            languages=["English"],
            available_days=[],
            initials="DT",
            about="Test doctor",
        )
        self.date = timezone.localdate() + timedelta(days=7)
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            weekday=self.date.weekday(),
            start_time=time(9, 0),
            end_time=time(12, 0),
            slot_duration_minutes=60,
        )
        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_appointment_belongs_to_authenticated_user(self):
        response = self.client.post(
            reverse("appointment-list"),
            {
                "doctorId": self.doctor.id,
                "phone": "+966500000000",
                "appointmentDate": self.date.isoformat(),
                "appointmentTime": "09:00 AM",
                "reason": "Routine consultation",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.get(id=response.data["id"])
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.patient_name, "Patient One")

    def test_user_cannot_read_another_users_appointment(self):
        appointment = Appointment.objects.create(
            user=self.other_user,
            doctor=self.doctor,
            patient_name="Patient Two",
            phone="+966511111111",
            email="two@example.com",
            appointment_date=self.date,
            appointment_time=time(10, 0),
            consultation_fee=150,
        )

        response = self.client.get(
            reverse("appointment-detail", args=[appointment.id]),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_past_appointment_cannot_be_cancelled(self):
        appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            patient_name="Patient One",
            phone="+966500000000",
            email="one@example.com",
            appointment_date=timezone.localdate() - timedelta(days=1),
            appointment_time=time(10, 0),
            consultation_fee=150,
            status=Appointment.Status.CONFIRMED,
        )

        response = self.client.post(
            reverse("appointment-cancel", args=[appointment.id]),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)

    def test_serializer_hides_cancel_for_past_appointment(self):
        appointment = Appointment.objects.create(
            user=self.user,
            doctor=self.doctor,
            patient_name="Patient One",
            phone="+966500000000",
            email="one@example.com",
            appointment_date=timezone.localdate() - timedelta(days=1),
            appointment_time=time(10, 0),
            consultation_fee=150,
            status=Appointment.Status.PENDING,
        )

        response = self.client.get(
            reverse("appointment-detail", args=[appointment.id]),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["canCancel"])
