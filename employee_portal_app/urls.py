from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    path('', views.employee_login, name='employee_login'),
    path('dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('upload-certificate/', views.upload_certificate, name='upload_certificate'),
    path('certificate/<int:certificate_id>/', views.view_certificate_status, name='certificate_status'),
    path('logout/', views.employee_logout, name='employee_logout'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
] 