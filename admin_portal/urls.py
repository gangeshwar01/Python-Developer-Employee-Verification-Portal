from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', LogoutView.as_view(next_page='admin_portal:admin_login'), name='admin_logout'),
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    
    # Employee URLs
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_add, name='employee_add'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('employees/<int:employee_id>/add-certificate/', views.add_certificate, name='add_certificate'),
    
    # Task URLs
    path('tasks/add/', views.task_add, name='task_add'),
    
    # Certificate URLs
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificates/<int:cert_id>/verify/', views.certificate_verify, name='certificate_verify'),
    path('certificates/<int:cert_id>/edit/', views.edit_certificate, name='edit_certificate'),
    path('certificates/<int:cert_id>/delete/', views.delete_certificate, name='delete_certificate'),
    path('certificates/<int:cert_id>/view/', views.view_certificate, name='view_certificate'),
    
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:department_id>/add-member/', views.add_department_member, name='add_department_member'),
    path('departments/<int:department_id>/delete-members/', views.delete_department_members, name='delete_department_members'),
    
    # User Group URLs
    path('user-groups/', views.user_group_list, name='user_group_list'),
    path('user-groups/add/', views.add_user_group, name='add_user_group'),
    path('user-groups/<int:group_id>/add-member/', views.add_group_member, name='add_group_member'),
    path('user-groups/<int:group_id>/add-competency/', views.add_competency, name='add_competency'),
    path('user-groups/<int:group_id>/members/<int:member_id>/add-competency/', views.add_member_competency, name='add_member_competency'),
    path('rate-competency/', views.rate_competency, name='rate_competency'),
    
    # Add new URL pattern for viewing certificate requests
    path('certificate-requests/', views.view_certificate_requests, name='view_certificate_requests'),
    path('certificate-requests/<int:request_id>/update-status/', views.update_certificate_request_status, name='update_certificate_request_status'),
    path('certificate-requests/<int:request_id>/delete/', views.delete_certificate_request, name='delete_certificate_request'),
] 