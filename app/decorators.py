from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def admin_required(function):
    @login_required(login_url='/login/')
    def wrap(request, *args, **kwargs):
        if request.user.role != 'admin':
            return HttpResponseForbidden("You do not have permission to access this page.")
        return function(request, *args, **kwargs)
    
    return wrap