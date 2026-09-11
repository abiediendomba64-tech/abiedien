from core.database import safe_execute


class Theme:
    """Theme model for managing color schemes and landing page sync."""

    @staticmethod
    def get_all():
        return safe_execute(
            "SELECT * FROM themes ORDER BY id DESC", fetch=True
        )

    @staticmethod
    def get_active():
        result = safe_execute(
            "SELECT * FROM themes WHERE is_active=1 LIMIT 1", fetch=True
        )
        return result[0] if result else None

    @staticmethod
    def get_by_id(theme_id):
        result = safe_execute(
            "SELECT * FROM themes WHERE id=?", (theme_id,), fetch=True
        )
        return result[0] if result else None

    @staticmethod
    def get_by_name(name):
        result = safe_execute(
            "SELECT * FROM themes WHERE name=?", (name,), fetch=True
        )
        return result[0] if result else None

    @staticmethod
    def create(name, primary_color, secondary_color, accent_color,
               bg_color, text_color, landing_template, landing_title,
               landing_subtitle, is_active=False):
        if is_active:
            safe_execute("UPDATE themes SET is_active=0")
        safe_execute("""
            INSERT INTO themes (name, primary_color, secondary_color, accent_color,
                                bg_color, text_color, landing_template, landing_title,
                                landing_subtitle, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, primary_color, secondary_color, accent_color,
              bg_color, text_color, landing_template, landing_title,
              landing_subtitle, 1 if is_active else 0))

    @staticmethod
    def update(theme_id, **kwargs):
        allowed = ['name', 'primary_color', 'secondary_color', 'accent_color',
                   'bg_color', 'text_color', 'landing_template', 'landing_title',
                   'landing_subtitle', 'landing_enabled']
        sets = []
        params = []
        for key, value in kwargs.items():
            if key in allowed:
                sets.append(f"{key}=?")
                params.append(value)
        if not sets:
            return
        params.append(theme_id)
        safe_execute(
            f"UPDATE themes SET {', '.join(sets)}, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            tuple(params)
        )

    @staticmethod
    def set_active(theme_id):
        safe_execute("UPDATE themes SET is_active=0")
        safe_execute("UPDATE themes SET is_active=1, updated_at=CURRENT_TIMESTAMP WHERE id=?", (theme_id,))

    @staticmethod
    def delete(theme_id):
        safe_execute("DELETE FROM themes WHERE id=?", (theme_id,))

    @staticmethod
    def get_landing_config():
        """Get the active landing page configuration for sync."""
        active = Theme.get_active()
        if not active:
            return None
        return {
            'template': active[8],
            'title': active[9],
            'subtitle': active[10],
            'enabled': bool(active[11]),
            'colors': {
                'primary': active[2],
                'secondary': active[3],
                'accent': active[4],
                'bg': active[5],
                'text': active[6],
            }
        }
