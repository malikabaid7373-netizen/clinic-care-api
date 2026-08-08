from datetime import time

from django.core.management.base import BaseCommand

from doctors.models import Doctor, DoctorAvailability


DOCTORS = [
    {
        "name": "Dr. Ahmed Al-Harbi",
        "specialty": "General Medicine",
        "qualification": "MBBS, MD General Medicine",
        "experience": 12,
        "rating": 4.9,
        "consultation_fee": 150,
        "languages": ["Arabic", "English"],
        "initials": "AH",
        "about": (
            "Dr. Ahmed provides general medical consultations, routine "
            "health examinations, diagnosis, and preventive healthcare."
        ),
        "available_days": ["Sunday", "Monday", "Tuesday", "Wednesday"],
    },
    {
        "name": "Dr. Sarah Al-Qahtani",
        "specialty": "Dentistry",
        "qualification": "BDS, MSc Dentistry",
        "experience": 9,
        "rating": 4.8,
        "consultation_fee": 200,
        "languages": ["Arabic", "English"],
        "initials": "SQ",
        "about": (
            "Dr. Sarah specializes in dental examinations, cleaning, "
            "restorative dentistry, and preventive oral healthcare."
        ),
        "available_days": ["Sunday", "Tuesday", "Thursday"],
    },
    {
        "name": "Dr. Mohammed Al-Otaibi",
        "specialty": "Pediatrics",
        "qualification": "MBBS, Arab Board Pediatrics",
        "experience": 15,
        "rating": 4.9,
        "consultation_fee": 180,
        "languages": ["Arabic", "English"],
        "initials": "MO",
        "about": (
            "Dr. Mohammed provides medical care for infants, children, and "
            "teenagers, including routine checkups and treatment."
        ),
        "available_days": ["Monday", "Wednesday", "Thursday"],
    },
    {
        "name": "Dr. Reem Al-Zahrani",
        "specialty": "Dermatology",
        "qualification": "MBBS, MD Dermatology",
        "experience": 8,
        "rating": 4.7,
        "consultation_fee": 220,
        "languages": ["Arabic", "English"],
        "initials": "RZ",
        "about": (
            "Dr. Reem specializes in diagnosing and treating skin, hair, "
            "and nail conditions using modern medical approaches."
        ),
        "available_days": ["Sunday", "Monday", "Wednesday"],
    },
    {
        "name": "Dr. Khalid Al-Shammari",
        "specialty": "Cardiology",
        "qualification": "MBBS, Fellowship in Cardiology",
        "experience": 18,
        "rating": 4.9,
        "consultation_fee": 300,
        "languages": ["Arabic", "English"],
        "initials": "KS",
        "about": (
            "Dr. Khalid specializes in heart health, cardiovascular "
            "diagnosis, preventive cardiology, and long-term patient care."
        ),
        "available_days": ["Tuesday", "Wednesday", "Thursday"],
    },
    {
        "name": "Dr. Nora Al-Dosari",
        "specialty": "Family Medicine",
        "qualification": "MBBS, Family Medicine",
        "experience": 7,
        "rating": 4.6,
        "consultation_fee": 140,
        "languages": ["Arabic", "English"],
        "initials": "ND",
        "about": (
            "Dr. Nora provides family healthcare, general consultations, "
            "routine checkups, and treatment for common conditions."
        ),
        "available_days": ["Sunday", "Monday", "Tuesday", "Thursday"],
    },
]

WEEKDAYS = {
    label: value
    for value, label in DoctorAvailability.Weekday.choices
}


class Command(BaseCommand):
    help = "Create or update portfolio doctors and weekly schedules."

    def handle(self, *args, **options):
        for doctor_data in DOCTORS:
            available_days = doctor_data["available_days"]
            defaults = {
                **doctor_data,
                "available_today": False,
                "is_active": True,
            }

            doctor, created = Doctor.objects.update_or_create(
                name=doctor_data["name"],
                defaults=defaults,
            )

            for day_name in available_days:
                DoctorAvailability.objects.get_or_create(
                    doctor=doctor,
                    weekday=WEEKDAYS[day_name],
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    defaults={
                        "slot_duration_minutes": 60,
                        "is_active": True,
                    },
                )

            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action}: {doctor.name}"))

        self.stdout.write(
            self.style.SUCCESS("Doctors and schedules seeded successfully."),
        )
