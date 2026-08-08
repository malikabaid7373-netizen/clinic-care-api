from datetime import time, timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor, DoctorAvailability


class DoctorApiTests(APITestCase):
    def setUp(self):
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

        selected_date = timezone.localdate() + timedelta(days=7)
        self.selected_date = selected_date
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            weekday=selected_date.weekday(),
            start_time=time(9, 0),
            end_time=time(12, 0),
            slot_duration_minutes=60,
        )

    def test_available_slots_are_generated(self):
        response = self.client.get(
            reverse("doctor-available-slots", args=[self.doctor.id]),
            {"date": self.selected_date.isoformat()},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slots"], [
            "09:00 AM",
            "10:00 AM",
            "11:00 AM",
        ])
