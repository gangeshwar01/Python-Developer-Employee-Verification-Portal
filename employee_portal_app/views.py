from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from admin_portal.models import Employee, Certificate, Task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from .forms import CertificateUploadForm
from .forms import EmployeeTaskForm
from django.views.decorators.http import require_POST
import logging
from .models import CertificateRequest
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
    tasks = Task.objects.filter(employee=employee).order_by('-date')
    certificates = Certificate.objects.filter(employee=employee).order_by('-upload_date')
    
    context = {
        'employee': employee,
        'tasks': tasks,
        'certificates': certificates,
    }
    return render(request, 'employee_portal/dashboard.html', context)

def upload_certificate(request):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    
    if request.method == 'POST':
        form = CertificateUploadForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.employee = employee
            certificate.status = 'pending'
            certificate.save()
            messages.success(request, 'Certificate uploaded successfully')
            return redirect('employee_portal:employee_dashboard')
    else:
        form = CertificateUploadForm()
    
    return render(request, 'employee_portal/upload_certificate.html', {'form': form})

def view_certificate_status(request, certificate_id):
    if 'employee_id' not in request.session:
        return redirect('employee_portal:employee_login')
    
    employee = get_object_or_404(Employee, id=request.session['employee_id'])
    certificate = get_object_or_404(Certificate, id=certificate_id, employee=employee)
    
    return render(request, 'employee_portal/certificate_status.html', {'certificate': certificate})

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
        messages.success(request, 'Task status updated.')
    return redirect('employee_portal:employee_dashboard')

@login_required
def certificate_request(request):
    if request.method == 'POST':
        cert_id = request.POST.get('certificate_id')
        message = request.POST.get('message')
        try:
            cert = Certificate.objects.get(id=cert_id, employee=request.user.employee)
            CertificateRequest.objects.create(employee=request.user.employee, certificate=cert, message=message)
            messages.success(request, 'Certificate request sent successfully.')
        except Certificate.DoesNotExist:
            messages.error(request, 'Invalid certificate selected.')
    return redirect('employee_portal:dashboard')
