from rest_framework.routers import DefaultRouter

from .views import PatientViewSet

router = DefaultRouter(use_regex_path=False)
router.register("", PatientViewSet, basename="patient")

urlpatterns = router.urls
