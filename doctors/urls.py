from rest_framework.routers import DefaultRouter

from doctors.views import DoctorViewSet


router = DefaultRouter()
router.register(
    prefix="doctors",
    viewset=DoctorViewSet,
    basename="doctor",
)

urlpatterns = router.urls