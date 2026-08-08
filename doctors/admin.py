from django.contrib import admin

from doctors.models import Doctor, DoctorAvailability


class DoctorAvailabilityInline(admin.TabularInline):
    model = DoctorAvailability
    extra = 1
    fields = (
        "weekday",
        "start_time",
        "end_time",
        "slot_duration_minutes",
        "is_active",
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "specialty",
        "consultation_fee",
        "rating",
        "is_active",
    )
    list_filter = ("specialty", "is_active")
    search_fields = ("name", "specialty", "qualification")
    ordering = ("id",)
    inlines = [DoctorAvailabilityInline]


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "doctor",
        "weekday_name",
        "start_time",
        "end_time",
        "slot_duration_minutes",
        "is_active",
    )
    list_filter = ("weekday", "is_active", "doctor")
    search_fields = ("doctor__name", "doctor__specialty")

    @admin.display(description="Day")
    def weekday_name(self, obj: DoctorAvailability) -> str:
        return obj.get_weekday_display()
