from datetime import datetime, timedelta

from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from appointments.models import Appointment
from doctors.models import Doctor, DoctorAvailability
from doctors.serializers import DoctorSerializer


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    queryset = Doctor.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "availabilities",
            queryset=DoctorAvailability.objects.filter(is_active=True).order_by(
                "weekday",
                "start_time",
            ),
        ),
    ).order_by("id")

    @action(detail=True, methods=["get"], url_path="available-slots")
    def available_slots(self, request, pk=None):
        doctor = self.get_object()
        date_value = request.query_params.get("date", "").strip()

        if not date_value:
            return Response(
                {"detail": "Date is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            selected_date = datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()
        if selected_date < today:
            return Response(
                {"detail": "Available slots cannot be requested for a past date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        availabilities = DoctorAvailability.objects.filter(
            doctor=doctor,
            weekday=selected_date.weekday(),
            is_active=True,
        ).order_by("start_time")

        booked_times = set(
            Appointment.objects.filter(
                doctor=doctor,
                appointment_date=selected_date,
            )
            .exclude(status=Appointment.Status.CANCELLED)
            .values_list("appointment_time", flat=True),
        )

        current_local_time = timezone.localtime().time()
        available_slots: set[str] = set()

        for availability in availabilities:
            slot_duration = timedelta(
                minutes=availability.slot_duration_minutes,
            )
            current_slot = datetime.combine(
                selected_date,
                availability.start_time,
            )
            availability_end = datetime.combine(
                selected_date,
                availability.end_time,
            )

            while current_slot + slot_duration <= availability_end:
                slot_time = current_slot.time().replace(microsecond=0)

                is_future_today = (
                    selected_date != today
                    or slot_time > current_local_time.replace(microsecond=0)
                )

                if slot_time not in booked_times and is_future_today:
                    available_slots.add(current_slot.strftime("%I:%M %p"))

                current_slot += slot_duration

        sorted_slots = sorted(
            available_slots,
            key=lambda value: datetime.strptime(value, "%I:%M %p"),
        )

        return Response(
            {
                "doctorId": doctor.id,
                "doctorName": doctor.name,
                "date": selected_date.isoformat(),
                "weekday": selected_date.strftime("%A"),
                "slots": sorted_slots,
            },
            status=status.HTTP_200_OK,
        )
