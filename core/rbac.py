"""
RBAC Configuration - Role & Permission Hierarchy
"""

# ================== ROLE HIERARCHY ==================
ROLES = {
    "super_admin": {
        "level": 5,
        "display": "🔴 Super Admin",
        "description": "Full system access"
    },
    "admin": {
        "level": 4,
        "display": "🟠 Admin",
        "description": "Manage members, tickets, forum"
    },
    "moderator": {
        "level": 3,
        "display": "🟡 Moderator",
        "description": "Moderate forum & tickets"
    },
    "member": {
        "level": 2,
        "display": "🟢 Member",
        "description": "Access forum, tickets, payment"
    },
    "new_user": {
        "level": 1,
        "display": "⚪ New User",
        "description": "Awaiting verification"
    }
}

# ================== PERMISSIONS PER ROLE ==================
PERMISSIONS = {
    "super_admin": {
        # System Management
        "system_settings": True,
        "manage_admins": True,
        "manage_moderators": True,
        "view_all_logs": True,
        "backup_database": True,
        "broadcast_all": True,
        
        # User Management
        "manage_users": True,
        "manual_verify_domain": True,
        "reset_user_data": True,
        "ban_unban_user": True,
        
        # Forum Management
        "delete_any_topic": True,
        "delete_any_reply": True,
        "lock_unlock_topic": True,
        "pin_unpin_topic": True,
        
        # Ticket Management
        "resolve_any_ticket": True,
        "reassign_ticket": True,
        "override_ticket_resolution": True,
        
        # Dashboard
        "view_system_analytics": True,
        "view_user_analytics": True,
        "view_payment_analytics": True,
        "export_reports": True,
    },
    
    "admin": {
        # User Management
        "manage_users": True,
        "manual_verify_domain": True,
        "ban_unban_user": True,
        "reset_user_password": True,
        
        # Forum Management
        "delete_topic_own_domain": True,
        "delete_reply_own_domain": True,
        "lock_unlock_topic_own_domain": True,
        "pin_unpin_topic_own_domain": True,
        
        # Ticket Management
        "resolve_ticket": True,
        "reassign_ticket_own_domain": True,
        "view_all_tickets": True,
        
        # Payment Review
        "review_payment_proof": True,
        "approve_reject_payment": True,
        
        # Dashboard
        "view_domain_analytics": True,
        "view_domain_users": True,
        "export_domain_reports": True,
        
        # Broadcast
        "broadcast_domain": True,
    },
    
    "moderator": {
        # Forum Moderation
        "delete_reply_own_domain": True,
        "lock_unlock_topic_own_domain": True,
        "pin_unpin_topic_own_domain": True,
        
        # Ticket Support
        "view_domain_tickets": True,
        "add_ticket_comment": True,
        "assign_ticket_to_self": True,
        
        # Dashboard
        "view_domain_dashboard": True,
        "view_domain_stats": True,
    },
    
    "member": {
        # Forum Access
        "create_topic": True,
        "create_reply": True,
        "edit_own_topic": True,
        "edit_own_reply": True,
        "delete_own_topic": True,
        "delete_own_reply": True,
        "view_forum": True,
        
        # Ticket System
        "create_ticket": True,
        "view_own_tickets": True,
        "add_comment_own_ticket": True,
        
        # Payment
        "submit_payment_proof": True,
        "view_payment_status": True,
        
        # Dashboard
        "view_personal_dashboard": True,
    },
    
    "new_user": {
        # Verification Only
        "view_verification_page": True,
        "submit_domain_verification": True,
        
        # Limited Access
        "view_forum_readonly": True,
        
        # Dashboard
        "view_registration_status": True,
    }
}

# ================== DOMAIN HIERARCHY ==================
# Setiap user punya domain, dan role bisa berbeda per domain
DOMAIN_ROLES = {
    "super_admin": {
        "can_manage_own_domain": True,
        "can_manage_other_domain": True,
        "can_create_subdomain": True,
    },
    "admin": {
        "can_manage_own_domain": True,
        "can_manage_other_domain": False,  # Hanya domain sendiri
        "can_create_subdomain": True,
    },
    "moderator": {
        "can_manage_own_domain": True,
        "can_manage_other_domain": False,
        "can_create_subdomain": False,
    },
    "member": {
        "can_manage_own_domain": False,
        "can_manage_other_domain": False,
        "can_create_subdomain": False,
    },
    "new_user": {
        "can_manage_own_domain": False,
        "can_manage_other_domain": False,
        "can_create_subdomain": False,
    }
}

# ================== HELPER FUNCTIONS ==================
def get_role_level(role):
    """Ambil level dari role (untuk sorting & hierarchy check)."""
    return ROLES.get(role, {}).get("level", 0)

def can_perform_action(user_role, permission):
    """Cek apakah user dengan role tertentu punya permission."""
    return PERMISSIONS.get(user_role, {}).get(permission, False)

def can_manage_domain(user_role, user_domain, target_domain):
    """Cek apakah user bisa manage domain tertentu."""
    # Super admin bisa manage semua domain
    if user_role == "super_admin":
        return True
    
    # Role lain hanya bisa manage domain sendiri
    if user_role in ["admin", "moderator"]:
        return user_domain == target_domain
    
    # Member & new_user tidak bisa manage
    return False

def has_higher_role(user_role, compare_role):
    """Cek apakah user_role lebih tinggi dari compare_role."""
    return get_role_level(user_role) > get_role_level(compare_role)

def get_accessible_domains(user_role, user_domains):
    """Ambil list domain yang accessible untuk user."""
    if user_role == "super_admin":
        return user_domains  # Semua domain
    else:
        return user_domains  # Hanya domain milik user (sesuai policy)
