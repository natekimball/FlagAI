from django.contrib import admin
from django.urls import path, include

from . import views
from .views import update_report_status

app_name = "flagai"
urlpatterns = [
    path("", views.index, name="index"),
    path('accounts/', include('allauth.urls')),
    path('admin/',  admin.site.urls),
    path('admin/login/', views.admin_login, name='admin_login'),
    path('delete/<str:report_id>/', views.delete_report, name='delete_report'),
    path('download/<str:file_id>/', views.download_file_from_s3, name='download_file'),
    path('login/', views.login_view, name="login"),
    path('login/anonymous', views.anonymous_login, name='anonymous_login'),
    path('logout/', views.logout_view, name="logout"),
    path('profile/', views.profile, name='profile'),
    path('reports/create/', views.create_report, name='create_report'),
    path('update_report_status/<int:report_id>/', update_report_status, name='update_report_status'),
    path('about/', views.about, name='about'),
]
