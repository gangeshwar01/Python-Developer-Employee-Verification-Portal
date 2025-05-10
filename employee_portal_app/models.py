from django.db import models
from admin_portal.models import Employee, Certificate

# Create your models here.

class CertificateRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='certificate_requests')
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='requests')
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Request by {self.employee.name} for {self.certificate.title}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('certificate_request', 'Certificate Request'),
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_completed', 'Task Completed'),
        ('general', 'General'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)  # To store ID of related object (task, certificate, etc.)

    def __str__(self):
        return f"{self.title} for {self.employee.name}"

    class Meta:
        ordering = ['-created_at']
