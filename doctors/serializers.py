from django.utils import timezone
from rest_framework import serializers

from doctors.models import Doctor, DoctorAvailability


class DoctorSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(read_only=True)
    consultationFee = serializers.FloatField(
        source="consultation_fee",
        read_only=True,
    )
    availableToday = serializers.SerializerMethodField()
    availableDays = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialty",
            "qualification",
            "experience",
            "rating",
            "consultationFee",
            "availableToday",
            "languages",
            "initials",
            "about",
            "availableDays",
        ]
        read_only_fields = fields

    def _active_availabilities(self, obj):
        prefetched = getattr(obj, "_prefetched_objects_cache", {}).get(
            "availabilities",
        )
        if prefetched is not None:
            return [item for item in prefetched if item.is_active]

        return list(obj.availabilities.filter(is_active=True))

    def get_availableToday(self, obj):
        weekday = timezone.localdate().weekday()
        return any(
            availability.weekday == weekday
            for availability in self._active_availabilities(obj)
        )

    def get_availableDays(self, obj):
        availabilities = self._active_availabilities(obj)

        if availabilities:
            weekday_map = dict(DoctorAvailability.Weekday.choices)
            weekdays = sorted({item.weekday for item in availabilities})
            return [weekday_map[weekday] for weekday in weekdays]

        return obj.available_days
