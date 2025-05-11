from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from .models import Employee, Task, Certificate, Department, UserGroup, GroupMember, Competency, DepartmentMember, SiteSettings
from .forms import EmployeeForm, TaskForm, CertificateVerificationForm, CertificateForm, SiteSettingsForm
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import url_has_allowed_host_and_scheme
import logging
from employee_portal_app.models import CertificateRequest, Notification
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

logger = logging.getLogger(__name__)

class AdminLoginView(LoginView):
    template_name = 'admin_portal/login.html'
    redirect_authenticated_user = True
    success_url = '/admin-portal/dashboard/'

    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, self.request.get_host()):
            return next_url
        return self.success_url

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            logger.info(f"Admin user {form.get_user().username} logged in successfully")
            return response
        except Exception as e:
            logger.error(f"Error during admin login: {str(e)}")
            messages.error(self.request, 'An error occurred during login. Please try again.')
            return self.form_invalid(form)

@login_required
def dashboard(request):
    department_count = Employee.objects.values('department').distinct().count()
    employee_count = Employee.objects.count()
    manager_count = Employee.objects.filter(designation__icontains='manager').count()
    performing_users_count = Employee.objects.filter(performance_rating__gte=4).count()
    
    context = {
        'department_count': department_count,
        'employee_count': employee_count,
        'manager_count': manager_count,
        'performing_users_count': performing_users_count,
        'performance_data': [65, 75, 70, 85, 80, 90, 88],  # Example data
        'performance_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']  # Example labels
    }
    return render(request, 'admin_portal/dashboard.html', context)

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    departments = Department.objects.all()
    return render(request, 'admin_portal/employee_list.html', {
        'employees': employees,
        'departments': departments
    })

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    logging.warning(f"[ADMIN PORTAL] Employee detail employee.id: {employee.id}, emp_id: {employee.emp_id}")
    tasks = Task.objects.filter(employee=employee).order_by('-date')
    certificates = Certificate.objects.filter(employee=employee)
    context = {
        'employee': employee,
        'tasks': tasks,
        'certificates': certificates,
    }
    return render(request, 'admin_portal/employee_detail.html', context)

@login_required
def employee_add(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save(commit=False)
            if 'profile_image' in request.FILES:
                employee.profile_image = request.FILES['profile_image']
            password = form.cleaned_data.get('password')
            if password:
                employee.set_password(password)
            employee.save()
            form.save_m2m()
            messages.success(request, 'Employee added successfully.')
            return redirect('admin_portal:employee_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            departments = Department.objects.all()
            return render(request, 'admin_portal/employee_list.html', {
                'employees': Employee.objects.all(),
                'departments': departments,
                'form_errors': form.errors
            })
    return redirect('admin_portal:employee_list')

@login_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            if 'profile_image' in request.FILES:
                employee.profile_image = request.FILES['profile_image']
            password = form.cleaned_data.get('password')
            if password:
                employee.set_password(password)
            employee.save()
            form.save_m2m()
            messages.success(request, 'Employee updated successfully.')
            return redirect('admin_portal:employee_detail', pk=pk)
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'admin_portal/employee_form.html', {'form': form, 'employee': employee})

@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('admin_portal:employee_list')
    return render(request, 'admin_portal/employee_confirm_delete.html', {'employee': employee})

@login_required
def task_add(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save()
            messages.success(request, 'Task added successfully.')
            return redirect('admin_portal:employee_detail', pk=task.employee.pk)
    else:
        form = TaskForm()
    
    return render(request, 'admin_portal/task_form.html', {
        'form': form,
        'title': 'Add Task'
    })

@login_required
def certificate_list(request):
    certificates = Certificate.objects.filter(status='pending').order_by('-upload_date')
    return render(request, 'admin_portal/certificate_list.html', {'certificates': certificates})

@login_required
def certificate_verify(request, cert_id):
    certificate = get_object_or_404(Certificate, id=cert_id)
    
    if request.method == 'POST':
        form = CertificateVerificationForm(request.POST, instance=certificate)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.verified_by = request.user
            cert.verification_date = timezone.now()
            if not cert.upload_date:
                cert.upload_date = timezone.now()
            cert.save()
            messages.success(request, 'Certificate verification status updated.')
            return redirect('admin_portal:certificate_list')
    else:
        form = CertificateVerificationForm(instance=certificate)
    
    context = {
        'form': form,
        'certificate': certificate,
        'title': 'Verify Certificate',
    }
    return render(request, 'admin_portal/certificate_verify.html', context)

@login_required
def department_list(request):
    departments = Department.objects.all()
    employees = Employee.objects.all()
    context = {
        'departments': departments,
        'employees': employees,
    }
    return render(request, 'admin_portal/department_list.html', context)

@login_required
def department_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Department.objects.create(name=name)
            messages.success(request, 'Department added successfully.')
            return redirect('admin_portal:department_list')
    return redirect('admin_portal:department_list')

@login_required
def user_group_list(request):
    groups = UserGroup.objects.all()
    employees = Employee.objects.all()
    context = {
        'groups': groups,
        'employees': employees,
    }
    return render(request, 'admin_portal/user_group_list.html', context)

@login_required
def add_user_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            UserGroup.objects.create(name=name)
            messages.success(request, 'User Group added successfully.')
        return redirect('admin_portal:user_group_list')
    return redirect('admin_portal:user_group_list')

@login_required
def add_group_member(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(UserGroup, id=group_id)
        employee_ids = request.POST.getlist('employee_ids')
        
        if employee_ids:
            for employee_id in employee_ids:
                employee = get_object_or_404(Employee, id=employee_id)
                # Check if member already exists in group
                if not GroupMember.objects.filter(group=group, employee=employee).exists():
                    GroupMember.objects.create(
                        name=employee.name,
                        group=group,
                        employee=employee
                    )
            messages.success(request, 'Members added successfully.')
        return redirect('admin_portal:user_group_list')
    return redirect('admin_portal:user_group_list')

@login_required
def add_competency(request, group_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        group = get_object_or_404(UserGroup, id=group_id)
        if name:
            Competency.objects.create(name=name, group=group)
            messages.success(request, 'Competency added successfully.')
        return redirect('admin_portal:user_group_list')
    return redirect('admin_portal:user_group_list')

@login_required
def add_member_competency(request, group_id, member_id):
    if request.method == 'POST':
        name = request.POST.get('name')
        group = get_object_or_404(UserGroup, id=group_id)
        member = get_object_or_404(GroupMember, id=member_id, group=group)
        if name:
            # Get or create the competency for this group
            competency, created = Competency.objects.get_or_create(name=name, group=group)
            member.competencies.add(competency)
            messages.success(request, 'Competency added to member successfully.')
        return redirect('admin_portal:user_group_list')
    return redirect('admin_portal:user_group_list')

@csrf_exempt
def rate_competency(request):
    if request.method == 'POST':
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_department_member(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    employees = Employee.objects.all()
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        name = request.POST.get('name')
        # Check for duplicate by employee or name
        if employee_id:
            employee = Employee.objects.get(id=employee_id)
            if DepartmentMember.objects.filter(department=department, name=employee.name).exists():
                messages.error(request, f'Member {employee.name} is already in this department.')
                return redirect('admin_portal:department_list')
            DepartmentMember.objects.create(name=employee.name, department=department)
            messages.success(request, f'Member {employee.name} added to department successfully.')
        elif name:
            if DepartmentMember.objects.filter(department=department, name=name).exists():
                messages.error(request, f'Member {name} is already in this department.')
                return redirect('admin_portal:department_list')
            DepartmentMember.objects.create(name=name, department=department)
            messages.success(request, f'Member {name} added to department successfully.')
        return redirect('admin_portal:department_list')
    return render(request, 'admin_portal/add_department_member.html', {'department': department, 'employees': employees})

@login_required
def delete_department_members(request, department_id):
    department = get_object_or_404(Department, id=department_id)
    if request.method == 'POST':
        member_ids = request.POST.getlist('member_ids')
        if member_ids:
            DepartmentMember.objects.filter(id__in=member_ids, department=department).delete()
            messages.success(request, 'Selected member(s) deleted from department.')
        else:
            messages.error(request, 'No members selected for deletion.')
        return redirect('admin_portal:department_list')
    # For GET, redirect to department list
    return redirect('admin_portal:department_list')

@login_required
def add_certificate(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.employee = employee
            cert.status = 'pending'
            cert.save()
            messages.success(request, 'Certificate uploaded successfully.')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('admin_portal:employee_detail', pk=employee_id)

@login_required
def edit_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, pk=cert_id)
    if request.method == 'POST':
        form = CertificateForm(request.POST, request.FILES, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate updated successfully.')
            return redirect('admin_portal:employee_detail', pk=cert.employee.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificateForm(instance=cert)
    return render(request, 'admin_portal/edit_certificate_modal.html', {'form': form, 'certificate': cert})

@login_required
def delete_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, pk=cert_id)
    employee_id = cert.employee.pk
    if request.method == 'POST':
        cert.delete()
        messages.success(request, 'Certificate deleted successfully.')
    return redirect('admin_portal:employee_detail', pk=employee_id)

@login_required
def view_certificate_requests(request):
    status_filter = request.GET.get('status', 'all')
    requests = CertificateRequest.objects.all().order_by('-created_at')
    
    if status_filter != 'all':
        requests = requests.filter(status=status_filter)
    
    # Count unread requests for the notification badge
    unread_requests_count = CertificateRequest.objects.filter(status='pending').count()
    
    context = {
        'requests': requests,
        'unread_requests_count': unread_requests_count,
    }
    return render(request, 'admin_portal/certificate_requests.html', context)

@login_required
@require_POST
def update_certificate_request_status(request, request_id):
    cert_request = get_object_or_404(CertificateRequest, id=request_id)
    status = request.POST.get('status')
    response_message = request.POST.get('response_message')
    
    if status in ['pending', 'in_progress', 'completed']:
        cert_request.status = status
        if response_message:
            # Create a notification for the employee
            Notification.objects.create(
                employee=cert_request.employee,
                title=f"Certificate Request Update: {cert_request.certificate.title}",
                message=response_message,
                notification_type='certificate_request'
            )
        cert_request.save()
        messages.success(request, 'Request status updated successfully.')
    else:
        messages.error(request, 'Invalid status selected.')
    
    return redirect('admin_portal:view_certificate_requests')

@login_required
@require_POST
def delete_certificate_request(request, request_id):
    cert_request = get_object_or_404(CertificateRequest, id=request_id)
    cert_request.delete()
    messages.success(request, 'Request deleted successfully.')
    return redirect('admin_portal:view_certificate_requests')

@login_required
def view_certificate(request, cert_id):
    certificate = get_object_or_404(Certificate, id=cert_id)
    return render(request, 'admin_portal/certificate_detail.html', {'certificate': certificate})

@require_POST
def update_employee_status(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    is_active = request.POST.get('is_active') == 'True'
    employee.is_active = is_active
    employee.save()
    return redirect('admin_portal:employee_detail', pk=pk)

@login_required
def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    # Mark notifications as read when viewed
    if request.method == 'GET':
        notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'title': 'Notifications'
    }
    return render(request, 'admin_portal/notification_list.html', context)

@login_required
@require_POST
def clear_all_notifications(request):
    Notification.objects.all().delete()
    messages.success(request, 'All notifications cleared.')
    return redirect('admin_portal:notification_list')

@login_required
@require_POST
def delete_notification(request, notification_id):
    Notification.objects.filter(id=notification_id).delete()
    messages.success(request, 'Notification removed.')
    return redirect('admin_portal:notification_list')

@login_required
def delete_user_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    group.delete()
    messages.success(request, 'User group deleted successfully.')
    return redirect('admin_portal:user_group_list')

@login_required
def delete_group_member(request, group_id, member_id):
    member = get_object_or_404(GroupMember, id=member_id, group_id=group_id)
    member.delete()
    messages.success(request, 'Member removed from group.')
    return redirect('admin_portal:user_group_list')

@login_required
def delete_member_competency(request, group_id, member_id, competency_id):
    member = get_object_or_404(GroupMember, id=member_id, group_id=group_id)
    member.competencies.remove(competency_id)
    messages.success(request, 'Competency removed from member.')
    return redirect('admin_portal:user_group_list')

@login_required
def delete_group_competency(request, group_id, competency_id):
    group = get_object_or_404(UserGroup, id=group_id)
    group.competencies.remove(competency_id)
    messages.success(request, 'Competency removed from group.')
    return redirect('admin_portal:user_group_list')

@login_required
def site_settings(request):
    settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    user = request.user
    username_error = None
    new_username = user.username
    if request.method == 'POST':
        settings_form = SiteSettingsForm(request.POST, request.FILES, instance=settings_obj)
        password_form = PasswordChangeForm(user, request.POST)
        new_username = request.POST.get('username', '').strip()
        if 'save_settings' in request.POST and settings_form.is_valid():
            # Handle username change
            if new_username and new_username != user.username:
                from django.contrib.auth.models import User
                if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                    username_error = 'This username is already taken.'
                else:
                    user.username = new_username
                    user.save()
                    messages.success(request, 'Username updated successfully.')
            if not username_error:
                settings_form.save()
                messages.success(request, 'Settings updated successfully.')
                return redirect('admin_portal:site_settings')
            # If there is a username error, fall through to re-render the page with the error
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully.')
            return redirect('admin_portal:site_settings')
    else:
        settings_form = SiteSettingsForm(instance=settings_obj)
        password_form = PasswordChangeForm(user)
    return render(request, 'admin_portal/site_settings.html', {
        'settings_form': settings_form,
        'password_form': password_form,
        'settings_obj': settings_obj,
        'username_error': username_error,
        'current_username': new_username,
    })
