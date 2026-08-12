from django.db.models import Q
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer


class AppointmentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Appointment.objects.select_related("doctor", "user").all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        queryset = self.get_queryset()
        today = timezone.localdate()
        current_time = timezone.localtime().time().replace(microsecond=0)
        upcoming = queryset.filter(
            Q(appointment_date__gt=today)
            | Q(appointment_date=today, appointment_time__gt=current_time),
            status__in=[
                Appointment.Status.PENDING,
                Appointment.Status.CONFIRMED,
            ],
        ).order_by("appointment_date", "appointment_time")

        next_appointment = upcoming.first()

        return Response(
            {
                "total": queryset.count(),
                "pending": queryset.filter(
                    status=Appointment.Status.PENDING,
                ).count(),
                "confirmed": queryset.filter(
                    status=Appointment.Status.CONFIRMED,
                ).count(),
                "completed": queryset.filter(
                    status=Appointment.Status.COMPLETED,
                ).count(),
                "cancelled": queryset.filter(
                    status=Appointment.Status.CANCELLED,
                ).count(),
                "upcoming": upcoming.count(),
                "nextAppointment": (
                    AppointmentSerializer(next_appointment).data
                    if next_appointment
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        appointment = self.get_object()

        if appointment.status == Appointment.Status.CANCELLED:
            return Response(
                {"detail": "Appointment is already cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment.status == Appointment.Status.COMPLETED:
            return Response(
                {"detail": "Completed appointment cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = timezone.localdate()
        current_time = timezone.localtime().time().replace(microsecond=0)
        is_future = (
            appointment.appointment_date > today
            or (
                appointment.appointment_date == today
                and appointment.appointment_time > current_time
            )
        )

        if not is_future:
            return Response(
                {"detail": "Past appointments cannot be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=["status", "updated_at"])

        return Response(
            self.get_serializer(appointment).data,
            status=status.HTTP_200_OK,
        )
