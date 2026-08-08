from django.conf import settings
from django.db import models

from doctors.models import Doctor


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
        blank=True,
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.PROTECT,
        related_name="appointments",
    )
    patient_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "appointment_date",
                    "appointment_time",
                ],
                condition=~models.Q(status="cancelled"),
                name="unique_active_doctor_appointment_slot",
            ),
        ]
        indexes = [
            models.Index(
                fields=["user", "appointment_date", "status"],
                name="appt_user_date_status_idx",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.patient_name} - {self.doctor.name} - "
            f"{self.appointment_date} {self.appointment_time}"
        )
