"""
RBAC (Role-Based Access Control) - Single Gate untuk semua pengecekan akses.

Hierarchy is canonical across the backend:
new_user(0) < member(1) < admin(2) < dev(3) < super_admin(4) < root(5)

Business permissions should use explicit helpers rather than assuming that
all operations available to a role are interchangeable.
"""

from functools import wraps
from typing import Callable, Any

from telebot import types

from core.bot import bot
from models.user import User


ROLE_HIERARCHY = {
    'new_user': 0,
    'member': 1,
    'admin': 2,
    'dev': 3,
    'super_admin': 4,
    'root': 5,
}

VALID_ROLES = frozenset(ROLE_HIERARCHY)


def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role, -1)


def has_access(user_role: str, required_role: str) -> bool:
    """Cek apakah user_role memiliki akses setara atau di atas required_role."""
    if user_role not in VALID_ROLES or required_role not in VALID_ROLES:
        return False
    return get_role_level(user_role) >= get_role_level(required_role)


def is_admin_or_higher(role: str) -> bool:
    return has_access(role, 'admin')


def is_dev_or_higher(role: str) -> bool:
    return has_access(role, 'dev')


def is_super_admin_or_higher(role: str) -> bool:
    return has_access(role, 'super_admin')


def is_root(role: str) -> bool:
    return role == 'root'


def can_manage_roles(role: str) -> bool:
    return role in {'super_admin', 'root'}


# Explicit operation permissions. Keep these centralized so handlers do not
# accidentally grant operational actions to member/new_user roles.
PERMISSIONS = {
    'ticket.create': 'member',
    'ticket.view': 'member',
    'ticket.assign': 'admin',
    'ticket.resolve': 'admin',
    'ticket.reply': 'admin',
    'ticket.priority': 'admin',
    'payment.submit': 'member',
    'payment.verify': 'admin',
    'system.operation': 'dev',
    'role.manage': 'super_admin',
    'emergency.recovery': 'root',
}


def can(role: str, permission: str) -> bool:
    """Check a named business permission against the canonical hierarchy."""
    required_role = PERMISSIONS.get(permission)
    if required_role is None:
        return False
    return has_access(role, required_role)


# ================== DECORATOR UNTUK HANDLER ==================
def require_role(min_role: str):
    """
    Decorator untuk membatasi akses handler berdasarkan minimum role.

    CallbackQuery dan Message ditangani secara eksplisit; jangan menggunakan
    keberadaan atribut reply_to sebagai type detection.
    """
    if min_role not in VALID_ROLES:
        raise ValueError(f"Unknown role: {min_role}")

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(message_or_call, *args, **kwargs):
            if isinstance(message_or_call, types.CallbackQuery):
                user_id = message_or_call.from_user.id
            elif isinstance(message_or_call, types.Message):
                user_id = message_or_call.from_user.id
            else:
                raise TypeError(
                    f"Unsupported handler object: {type(message_or_call).__name__}"
                )

            role = User.get_role(user_id)
            if has_access(role, min_role):
                return func(message_or_call, *args, **kwargs)

            error_msg = (
                f"⛔ Akses ditolak. Role Anda: {role}. "
                f"Dibutuhkan: {min_role} atau lebih tinggi."
            )

            if isinstance(message_or_call, types.CallbackQuery):
                bot.answer_callback_query(
                    message_or_call.id,
                    error_msg,
                    show_alert=True,
                )
            else:
                bot.reply_to(message_or_call, error_msg)
            return None

        return wrapper
    return decorator


def require_permission(permission: str):
    """Decorator untuk permission bisnis yang lebih spesifik dari minimum role."""
    if permission not in PERMISSIONS:
        raise ValueError(f"Unknown permission: {permission}")

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(message_or_call, *args, **kwargs):
            if isinstance(message_or_call, types.CallbackQuery):
                user_id = message_or_call.from_user.id
            elif isinstance(message_or_call, types.Message):
                user_id = message_or_call.from_user.id
            else:
                raise TypeError(
                    f"Unsupported handler object: {type(message_or_call).__name__}"
                )

            role = User.get_role(user_id)
            if can(role, permission):
                return func(message_or_call, *args, **kwargs)

            error_msg = f"⛔ Akses ditolak untuk operasi: {permission}."
            if isinstance(message_or_call, types.CallbackQuery):
                bot.answer_callback_query(
                    message_or_call.id,
                    error_msg,
                    show_alert=True,
                )
            else:
                bot.reply_to(message_or_call, error_msg)
            return None

        return wrapper
    return decorator
