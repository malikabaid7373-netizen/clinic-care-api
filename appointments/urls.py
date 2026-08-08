from rest_framework.routers import DefaultRouter

from appointments.views import AppointmentViewSet


router = DefaultRouter()

router.register(
    prefix="appointments",
    viewset=AppointmentViewSet,
    basename="appointment",
)

urlpatterns = router.urls