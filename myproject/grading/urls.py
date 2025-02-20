from django.urls import path
from .views import upload_code
from . import views
from .views import register_view, login_view, logout_view, dashboard_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('upload/', upload_code, name='upload_code'),
    path('', views.home, name='home'),
]
