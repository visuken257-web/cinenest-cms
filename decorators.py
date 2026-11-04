# Chapter 7: Roles & Permissions
# Custom decorator co tham so: permission_required(perm) va admin_required.

from functools import wraps
from flask import abort
from flask_login import current_user
from models import Permission


def permission_required(permission):
    """
    Decorator co tham so - phai co 1 lop ham "factory" ben ngoai de nhan tham so `permission`,
    ben trong moi la decorator thuc su boc quanh view function.
    """
    def decorator(f):
        @wraps(f)  # @wraps giu nguyen __name__/__doc__ cua view function goc (quan trong cho url_for & debug)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # chua dang nhap
            if not current_user.can(permission):
                abort(403)  # da dang nhap nhung khong du quyen
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)


def owner_or_admin_required(get_owner_id):
    """
    Decorator kiem tra quyen so huu tai nguyen (resource ownership) - chong IDOR.
    `get_owner_id(*args, **kwargs)` la ham tra ve owner_id cua tai nguyen dang duoc truy cap,
    nhan cung tham so voi view function (vi du book_id trong URL).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            owner_id = get_owner_id(*args, **kwargs)
            if current_user.id != owner_id and not current_user.is_admin():
                abort(403, description="Bạn không sở hữu tài nguyên này.")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
