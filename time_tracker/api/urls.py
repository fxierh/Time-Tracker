from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from .views import CreateUserView, ManageUserView, StageViewSet, DayViewSet, SessionViewSet, SubjectViewSet

app_name = 'api'

# Routing: correspondence between urls and viewset
router = DefaultRouter()
router.register('stages', StageViewSet)
router.register('days', DayViewSet)
router.register('sessions', SessionViewSet)
router.register('subjects', SubjectViewSet)

urlpatterns = [
    # OpenAPI 3.0 schema & docs (Swagger UI)
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='docs'),

    # Endpoint to get a token for authentication
    path('token/', obtain_auth_token, name='token'),

    # Endpoints for creating user
    path('users/', CreateUserView.as_view(), name='create_user'),

    # Endpoints for getting, updating and deleting the authenticated user
    path('me/', ManageUserView.as_view(), name='me'),

    # Endpoints for CRUD operations on the stages, days, sessions and subjects of the authenticated user
    path('', include(router.urls))
]
