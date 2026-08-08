from datetime import datetime, timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import serializers

from appointments.models import Appointment
from doctors.models import Doctor, DoctorAvailability


class AppointmentSerializer(serializers.ModelSerializer):
    doctorId = serializers.PrimaryKeyRelatedField(
        source="doctor",
        queryset=Doctor.objects.filter(is_active=True),
    )
    doctorName = serializers.CharField(source="doctor.name", read_only=True)
    doctorInitials = serializers.CharField(
        source="doctor.initials",
        read_only=True,
    )
    specialty = serializers.CharField(
        source="doctor.specialty",
        read_only=True,
    )
    patientName = serializers.CharField(
        source="patient_name",
        read_only=True,
    )
    appointmentDate = serializers.DateField(source="appointment_date")
    appointmentTime = serializers.TimeField(
        source="appointment_time",
        input_formats=["%I:%M %p", "%H:%M", "%H:%M:%S"],
        format="%I:%M %p",
    )
    consultationFee = serializers.DecimalField(
        source="consultation_fee",
        max_digits=8,
        decimal_places=2,
        read_only=True,
    )
    statusLabel = serializers.CharField(
        source="get_status_display",
        read_only=True,
    )
    canCancel = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctorId",
            "doctorName",
            "doctorInitials",
            "specialty",
            "patientName",
            "phone",
            "email",
            "appointmentDate",
            "appointmentTime",
            "reason",
            "status",
            "statusLabel",
            "canCancel",
            "consultationFee",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = [
            "id",
            "patientName",
            "email",
            "status",
            "statusLabel",
            "canCancel",
            "consultationFee",
            "createdAt",
            "updatedAt",
        ]

    def get_canCancel(self, obj):
        return obj.status in {
            Appointment.Status.PENDING,
            Appointment.Status.CONFIRMED,
        }

    def validate_phone(self, value):
        phone = "".join(character for character in value.strip() if character not in " -()")

        if phone.startswith("+"):
            digits = phone[1:]
        else:
            digits = phone

        if not digits.isdigit() or not 8 <= len(digits) <= 15:
            raise serializers.ValidationError("Enter a valid phone number.")

        return phone

    def validate(self, attrs):
        doctor = attrs["doctor"]
        appointment_date = attrs["appointment_date"]
        appointment_time = attrs["appointment_time"].replace(microsecond=0)
        today = timezone.localdate()

        if appointment_date < today:
            raise serializers.ValidationError(
                {"appointmentDate": "Appointment date cannot be in the past."},
            )

        if (
            appointment_date == today
            and appointment_time <= timezone.localtime().time().replace(microsecond=0)
        ):
            raise serializers.ValidationError(
                {"appointmentTime": "Appointment time must be in the future."},
            )

        availabilities = DoctorAvailability.objects.filter(
            doctor=doctor,
            weekday=appointment_date.weekday(),
            is_active=True,
            start_time__lte=appointment_time,
            end_time__gt=appointment_time,
        )

        selected_datetime = datetime.combine(
            appointment_date,
            appointment_time,
        )
        valid_slot = False

        for availability in availabilities:
            start_datetime = datetime.combine(
                appointment_date,
                availability.start_time,
            )
            end_datetime = datetime.combine(
                appointment_date,
                availability.end_time,
            )
            difference_minutes = int(
                (selected_datetime - start_datetime).total_seconds() // 60,
            )
            slot_duration = availability.slot_duration_minutes
            slot_end_datetime = selected_datetime + timedelta(
                minutes=slot_duration,
            )

            if (
                difference_minutes >= 0
                and difference_minutes % slot_duration == 0
                and slot_end_datetime <= end_datetime
            ):
                valid_slot = True
                break

        if not valid_slot:
            day_name = appointment_date.strftime("%A")
            raise serializers.ValidationError(
                {
                    "appointmentTime": (
                        f"{doctor.name} is not available at this time on "
                        f"{day_name}."
                    ),
                },
            )

        slot_exists = (
            Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
            )
            .exclude(status=Appointment.Status.CANCELLED)
            .exists()
        )

        if slot_exists:
            raise serializers.ValidationError(
                {"appointmentTime": "This appointment slot is already booked."},
            )

        attrs["appointment_time"] = appointment_time
        return attrs

    def create(self, validated_data):
        doctor = validated_data["doctor"]
        user = validated_data["user"]
        full_name = str(getattr(user, "first_name", "")).strip()

        validated_data["patient_name"] = full_name or user.get_username()
        validated_data["email"] = str(getattr(user, "email", "")).strip()
        validated_data["consultation_fee"] = doctor.consultation_fee

        try:
            with transaction.atomic():
                return super().create(validated_data)
        except IntegrityError as error:
            raise serializers.ValidationError(
                {
                    "appointmentTime": (
                        "This appointment slot was just booked by another patient."
                    ),
                },
            ) from error
