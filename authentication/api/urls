from rest_framework.routers import SimpleRouter

from .viewsets import StudentAuthViewSet, CodeConfirmViewSet

router = SimpleRouter() # pylint: disable=invalid-name
router.register(r'api/auth/student', StudentAuthViewSet)
router.register(r'api/auth/confirm', CodeConfirmViewSet)
urlpatterns = router.urls
