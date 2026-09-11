import secrets
from core.database import safe_execute


class PanelAccount:
    """Panel backoffice account model for domain ownership registration."""

    @staticmethod
    def get_all(limit=50):
        return safe_execute("""
            SELECT pa.*, u.full_name, u.telegram_username
            FROM panel_accounts pa
            LEFT JOIN users u ON pa.user_id = u.telegram_id
            ORDER BY pa.id DESC LIMIT ?
        """, (limit,), fetch=True)

    @staticmethod
    def get_by_user(user_id):
        result = safe_execute(
            "SELECT * FROM panel_accounts WHERE user_id=?", (user_id,), fetch=True
        )
        return result[0] if result else None

    @staticmethod
    def get_by_id(panel_id):
        result = safe_execute("""
            SELECT pa.*, u.full_name, u.telegram_username
            FROM panel_accounts pa
            LEFT JOIN users u ON pa.user_id = u.telegram_id
            WHERE pa.id = ?
        """, (panel_id,), fetch=True)
        return result[0] if result else None

    @staticmethod
    def create(user_id, domain, panel_username=None, panel_password=None, panel_url='/backoffice'):
        # Generate random credentials if not provided
        if not panel_username:
            panel_username = f"user_{user_id}"
        if not panel_password:
            panel_password = secrets.token_urlsafe(12)
        
        existing = PanelAccount.get_by_user(user_id)
        if existing:
            safe_execute("""
                UPDATE panel_accounts
                SET domain=?, panel_username=?, panel_password=?, panel_url=?, status='active', updated_at=CURRENT_TIMESTAMP
                WHERE user_id=?
            """, (domain, panel_username, panel_password, panel_url, user_id))
        else:
            safe_execute("""
                INSERT INTO panel_accounts (user_id, domain, panel_username, panel_password, panel_url, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (user_id, domain, panel_username, panel_password, panel_url))
        
        return PanelAccount.get_by_user(user_id)

    @staticmethod
    def update(panel_id, **kwargs):
        allowed = ['domain', 'panel_username', 'panel_password', 'panel_url', 'status']
        sets = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                sets.append(f"{key}=?")
                params.append(value)
        if not sets:
            return
        params.append(panel_id)
        safe_execute(
            f"UPDATE panel_accounts SET {', '.join(sets)}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            tuple(params)
        )

    @staticmethod
    def delete(panel_id):
        safe_execute("DELETE FROM panel_accounts WHERE id=?", (panel_id,))
