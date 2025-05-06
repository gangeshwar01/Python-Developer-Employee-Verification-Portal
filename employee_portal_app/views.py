from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from admin_portal.models import Employee, Certificate, Task
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from .forms import CertificateUploadForm
import logging

logger = logging.getLogger(__name__)

def employee_login(request):
    if request.method == 'POST':
        emp_id = request.POST.get('emp_id')
        try:
            employee = Employee.objects.get(emp_id=emp_id)
            request.session['employee_id'] = employee.id
            logger.info(f"Employee {emp_id} logged in successfully")
            return redirect('employee_portal:employee_dashboard')
        except Employee.DoesNotExist:
            logger.warning(f"Failed login attempt for employee ID: {emp_id}")
            messages.error(request, 'Invalid Employee ID')
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
