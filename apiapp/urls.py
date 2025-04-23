from rest_framework.routers import DefaultRouter
from apiapp.views import TaskViewSet, user_signup, get_jwt_token
from django.urls import path

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
urlpatterns = [
    path('user-signup/', user_signup, name='user-signup'),
    path('token/', get_jwt_token, name='get-jwt-token'),
] + router.urls
