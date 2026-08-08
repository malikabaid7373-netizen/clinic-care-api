from datetime import timedelta, time

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment
from doctors.models import Doctor, DoctorAvailability


User = get_user_model()

DEMO_EMAIL = "demo@cliniccare.local"
DEMO_PASSWORD = "ClinicDemo@123"


def next_date_for_weekday(start_date, weekday):
    days_ahead = (weekday - start_date.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return start_date + timedelta(days=days_ahead)


def previous_date_for_weekday(start_date, weekday):
    days_back = (start_date.weekday() - weekday) % 7
    if days_back == 0:
        days_back = 7
    return start_date - timedelta(days=days_back)


class Command(BaseCommand):
    help = "Create a local demo patient and portfolio appointment history."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username=DEMO_EMAIL,
            defaults={
                "email": DEMO_EMAIL,
                "first_name": "Demo Patient",
                "is_active": True,
            },
        )
        user.email = DEMO_EMAIL
        user.first_name = "Demo Patient"
        user.is_active = True
        user.set_password(DEMO_PASSWORD)
        user.save()

        doctors = list(Doctor.objects.filter(is_active=True).order_by("id"))
        if len(doctors) < 4:
            self.stderr.write(
                self.style.ERROR("Run python manage.py seed_doctors first."),
            )
            return

        today = timezone.localdate()

        demo_rows = [
            {
                "doctor": doctors[0],
                "date": next_date_for_weekday(today, 0),
                "time": time(10, 0),
                "status": Appointment.Status.CONFIRMED,
                "reason": "General wellness consultation and preventive checkup.",
            },
            {
                "doctor": doctors[1],
                "date": next_date_for_weekday(today, 1),
                "time": time(11, 0),
                "status": Appointment.Status.PENDING,
                "reason": "Routine dental examination.",
            },
            {
                "doctor": doctors[3],
                "date": previous_date_for_weekday(today, 2),
                "time": time(14, 0),
                "status": Appointment.Status.COMPLETED,
                "reason": "Skin consultation and follow-up review.",
            },
        ]

        created_count = 0
        for row in demo_rows:
            doctor = row["doctor"]
            appointment_date = row["date"]
            appointment_time = row["time"]

            # Ensure the demo time is inside an existing schedule. If not, create
            # a portfolio schedule for that weekday.
            DoctorAvailability.objects.get_or_create(
                doctor=doctor,
                weekday=appointment_date.weekday(),
                start_time=time(9, 0),
                end_time=time(17, 0),
                defaults={
                    "slot_duration_minutes": 60,
                    "is_active": True,
                },
            )

            _, created = Appointment.objects.update_or_create(
                user=user,
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                defaults={
                    "patient_name": "Demo Patient",
                    "phone": "+966500000001",
                    "email": DEMO_EMAIL,
                    "reason": row["reason"],
                    "status": row["status"],
                    "consultation_fee": doctor.consultation_fee,
                },
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo account ready: {DEMO_EMAIL} / {DEMO_PASSWORD}",
            ),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo appointment data prepared ({created_count} new rows).",
            ),
        )
