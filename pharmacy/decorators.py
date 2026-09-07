from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_employee_or_admin():
            raise PermissionDenied("ليس لديك الصلاحيات الكافية للوصول إلى لوحة ERP.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view