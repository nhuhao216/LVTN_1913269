from django.http import HttpResponse
from django.shortcuts import redirect
from .models import *


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()
            if len(group) > 2 and any(role.name in allowed_roles for role in group):
                return view_func(request, *args, **kwargs)
            elif group[0].name in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Not authorized')
        return wrapper_func
    return decorator

def non_admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'quanly':
            return redirect('quanli_dspr')
        else:
            print(group)
            return view_func(request, *args, **kwargs)
    return wrapper_function