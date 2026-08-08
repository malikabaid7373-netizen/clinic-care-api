from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


admin.site.site_header = "ClinicCare Administration"
admin.site.site_title = "ClinicCare Admin"
admin.site.index_title = "Clinic operations"


def health_check(_request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "ClinicCare API",
        },
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("doctors.urls")),
    path("api/", include("appointments.urls")),
]
