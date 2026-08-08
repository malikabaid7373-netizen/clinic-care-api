from django.contrib import admin
from django.utils import timezone

from appointments.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "patient_name",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "consultation_fee",
    )
    list_filter = ("status", "appointment_date", "doctor")
    search_fields = (
        "patient_name",
        "phone",
        "email",
        "user__username",
        "user__email",
        "doctor__name",
    )
    readonly_fields = (
        "user",
        "patient_name",
        "email",
        "consultation_fee",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    date_hierarchy = "appointment_date"
    list_select_related = ("doctor", "user")
    actions = (
        "mark_confirmed",
        "mark_completed",
        "mark_cancelled",
    )

    @admin.action(description="Mark selected appointments as confirmed")
    def mark_confirmed(self, request, queryset):
        updated = queryset.filter(
            status=Appointment.Status.PENDING,
        ).update(
            status=Appointment.Status.CONFIRMED,
            updated_at=timezone.now(),
        )
        self.message_user(request, f"{updated} appointment(s) confirmed.")

    @admin.action(description="Mark selected appointments as completed")
    def mark_completed(self, request, queryset):
        updated = queryset.filter(
            status=Appointment.Status.CONFIRMED,
        ).update(
            status=Appointment.Status.COMPLETED,
            updated_at=timezone.now(),
        )
        self.message_user(request, f"{updated} appointment(s) completed.")

    @admin.action(description="Mark selected appointments as cancelled")
    def mark_cancelled(self, request, queryset):
        updated = queryset.exclude(
            status=Appointment.Status.COMPLETED,
        ).update(
            status=Appointment.Status.CANCELLED,
            updated_at=timezone.now(),
        )
        self.message_user(request, f"{updated} appointment(s) cancelled.")
