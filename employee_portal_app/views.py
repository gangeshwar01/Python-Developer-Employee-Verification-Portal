from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from admin_portal.models import Employee, Certificate, Task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from .forms import CertificateUploadForm
from .forms import EmployeeTaskForm
from django.views.decorators.http import require_POST
import logging
from .models import CertificateRequest, Notification
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

def employee_login(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        password = request.POST.get('password')
        try:
            employee = Employee.objects.get(emp_id=emp_id)
            if not password or not employee.check_password(password):
                messages.error(request, 'Invalid Employee ID or Password')
                return render(request, 'employee_portal/login.html')
            request.session['employee_id'] = employee.id
            logger.info(f"Employee {emp_id} logged in successfully")
            return redirect('employee_portal:employee_dashboard')
        except Employee.DoesNotExist:
            logger.warning(f"Failed login attempt for employee ID: {emp_id}")
            messages.error(request, 'Invalid Employee ID or Password')
        except Exception as e:
            logger.error(f"Error during employee login: {str(e)}")
            messages.error(request, 'An error occurred during login. Please try again.')
    return render(request, 'employee_portal/login.html')

def employee_dashboard(request):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    logging.warning(f"[EMPLOYEE PORTAL] Dashboard employee.id: {employee.id}, emp_id: {employee.emp_id}")
    tasks = Task.objects.filter(employee=employee).order_by('-date')
    certificates = Certificate.objects.filter(employee=employee).order_by('-upload_date')
    
    context = {
        'employee': employee,
        'tasks': tasks,
        'certificates': certificates,
    }
    return render(request, 'employee_portal/dashboard.html', context)

def employee_logout(request):
    if 'employee_id' in request.session:
        del request.session['employee_id']
    return redirect('employee_portal:employee_login')

def add_task(request):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.employee = employee
            task.save()
            # Create notification for admin
            Notification.objects.create(
                employee=employee,
                title="New Task Created",
                message=f"Task '{task.title}' has been created",
                notification_type='task_created',
                related_object_id=task.id
            )
            messages.success(request, 'Task added successfully.')
            return redirect('employee_portal:employee_dashboard')
    else:
        form = EmployeeTaskForm()
    return render(request, 'employee_portal/task_form.html', {'form': form, 'title': 'Add Task'})

def edit_task(request, task_id):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    task = get_object_or_404(Task, id=task_id, employee=employee)
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            # Create notification for admin
            Notification.objects.create(
                employee=employee,
                title="Task Updated",
                message=f"Task '{task.title}' has been updated",
                notification_type='task_updated',
                related_object_id=task.id
            )
            messages.success(request, 'Task updated successfully.')
            return redirect('employee_portal:employee_dashboard')
    else:
        form = EmployeeTaskForm(instance=task)
    return render(request, 'employee_portal/task_form.html', {'form': form, 'title': 'Edit Task'})

@require_POST
def delete_task(request, task_id):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    task = get_object_or_404(Task, id=task_id, employee=employee)
    task.delete()
    messages.success(request, 'Task deleted successfully.')
    return redirect('employee_portal:employee_dashboard')

@require_POST
def update_task_status(request, task_id):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    task = get_object_or_404(Task, id=task_id, employee=employee)
    status = request.POST.get('status')
    if status in dict(Task.STATUS_CHOICES):
        task.status = status
        task.save()
        # Create notification for admin
        Notification.objects.create(
            employee=employee,
            title="Task Status Updated",
            message=f"Task '{task.title}' status changed to '{task.get_status_display()}'",
            notification_type='task_updated',
            related_object_id=task.id
        )
        messages.success(request, 'Task status updated.')
    return redirect('employee_portal:employee_dashboard')

@login_required
def certificate_request(request):
    if request.method == 'POST':
        cert_id = request.POST.get('certificate_id')
        message = request.POST.get('message')
        employee = get_object_or_404(Employee, id=request.session['employee_id'])
        try:
            cert = Certificate.objects.get(id=cert_id, employee=employee)
            CertificateRequest.objects.create(employee=employee, certificate=cert, message=message)
            # Create notification for admin
            Notification.objects.create(
                employee=employee,
                title="Certificate/Message Request",
                message=f"{employee.name} sent a certificate/message request: {message}",
                notification_type='certificate_request',
                related_object_id=cert.id
            )
            messages.success(request, 'Certificate request sent successfully.')
        except Certificate.DoesNotExist:
            messages.error(request, 'Invalid certificate selected.')
    return redirect('employee_portal:employee_dashboard')

@login_required
def create_task(request):
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.employee = request.user.employee
            task.save()
            
            # Create notification for admin
            Notification.objects.create(
                employee=request.user.employee,
                title="New Task Created",
                message=f"Task '{task.title}' has been created",
                notification_type='task_created',
                related_object_id=task.id
            )
            
            messages.success(request, 'Task created successfully!')
            return redirect('employee_portal:employee_dashboard')
    else:
        form = EmployeeTaskForm()
    return render(request, 'employee_portal/create_task.html', {'form': form})

@login_required
def update_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, employee=request.user.employee)
    if request.method == 'POST':
        form = EmployeeTaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            
            # Create notification for admin
            Notification.objects.create(
                employee=request.user.employee,
                title="Task Updated",
                message=f"Task '{task.title}' has been updated",
                notification_type='task_updated',
                related_object_id=task.id
            )
            
            messages.success(request, 'Task updated successfully!')
            return redirect('employee_portal:employee_dashboard')
    else:
        form = EmployeeTaskForm(instance=task)
    return render(request, 'employee_portal/update_task.html', {'form': form})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, employee=request.user.employee)
    task.status = 'completed'
    task.save()
    
    # Create notification for admin
    Notification.objects.create(
        employee=request.user.employee,
        title="Task Completed",
        message=f"Task '{task.title}' has been marked as completed",
        notification_type='task_completed',
        related_object_id=task.id
    )
    
    messages.success(request, 'Task marked as completed!')
    return redirect('employee_portal:employee_dashboard')
