from rest_framework.routers import DefaultRouter
from apiapp.views import TaskViewSet, user_signup
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
urlpatterns = [
    path('user-signup/', user_signup, name='user-signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] + router.urls
