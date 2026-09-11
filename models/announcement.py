from core.database import safe_execute


class Announcement:
    """Announcement model for admin-to-member information sync."""

    @staticmethod
    def get_all(limit=20):
        return safe_execute("""
            SELECT * FROM announcements ORDER BY id DESC LIMIT ?
        """, (limit,), fetch=True)

    @staticmethod
    def get_by_id(ann_id):
        result = safe_execute(
            "SELECT * FROM announcements WHERE id=?", (ann_id,), fetch=True
        )
        return result[0] if result else None

    @staticmethod
    def get_for_role(role):
        """Get announcements targeted to a specific role."""
        return safe_execute("""
            SELECT * FROM announcements
            WHERE target_role IS NULL OR target_role = ? OR target_role = 'all'
            ORDER BY id DESC LIMIT 20
        """, (role,), fetch=True)

    @staticmethod
    def create(admin_id, title, content, target_role=None):
        safe_execute("""
            INSERT INTO announcements (admin_id, title, content, target_role)
            VALUES (?, ?, ?, ?)
        """, (admin_id, title, content, target_role))

    @staticmethod
    def delete(ann_id):
        safe_execute("DELETE FROM announcements WHERE id=?", (ann_id,))
