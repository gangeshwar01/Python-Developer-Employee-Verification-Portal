from django.contrib import admin
from .models import Employee, Task, Certificate

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('emp_id', 'name', 'designation', 'join_date')
    search_fields = ('emp_id', 'name', 'designation')
    list_filter = ('designation', 'join_date')
    ordering = ('emp_id',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'date')
    search_fields = ('employee__name', 'title', 'description')
    list_filter = ('date', 'employee')
    ordering = ('-date',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'status', 'upload_date', 'verified_by')
    search_fields = ('employee__name', 'title')
    list_filter = ('status', 'upload_date', 'verification_date')
    ordering = ('-upload_date',)
    readonly_fields = ('upload_date',)
