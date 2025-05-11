from employee_portal_app.models import Notification
from .models import SiteSettings

def notification_count(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(is_read=False).count()
        return {'unread_count': unread_count}
    return {'unread_count': 0}

def site_settings(request):
    settings_obj, _ = SiteSettings.objects.get_or_create(pk=1)
    return {'settings_obj': settings_obj} 