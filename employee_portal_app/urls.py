from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    path('', views.employee_login, name='employee_login'),
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('upload-certificate/', views.upload_certificate, name='upload_certificate'),
    path('certificate/<int:certificate_id>/', views.view_certificate_status, name='certificate_status'),
    path('logout/', views.employee_logout, name='employee_logout'),
] 