from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialty = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    experience = models.PositiveSmallIntegerField()
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
    )
    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    available_today = models.BooleanField(default=False)
    languages = models.JSONField(default=list)
    available_days = models.JSONField(default=list)
    initials = models.CharField(max_length=10)
    about = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.name} - {self.specialty}"


class DoctorAvailability(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="availabilities",
    )
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveSmallIntegerField(
        default=30,
        validators=[
            MinValueValidator(5),
            MaxValueValidator(240),
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["doctor_id", "weekday", "start_time"]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "doctor",
                    "weekday",
                    "start_time",
                    "end_time",
                ],
                name="unique_doctor_weekly_availability",
            ),
        ]

    def clean(self):
        super().clean()

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {"end_time": "End time must be later than start time."},
            )

        if not all([self.doctor_id, self.weekday is not None, self.start_time, self.end_time]):
            return

        overlap = DoctorAvailability.objects.filter(
            doctor_id=self.doctor_id,
            weekday=self.weekday,
            is_active=True,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if self.is_active and overlap.exists():
            raise ValidationError(
                "This schedule overlaps another active schedule for the doctor.",
            )

    def __str__(self) -> str:
        return (
            f"{self.doctor.name} - "
            f"{self.get_weekday_display()} - "
            f"{self.start_time.strftime('%I:%M %p')} to "
            f"{self.end_time.strftime('%I:%M %p')}"
        )
