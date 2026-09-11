import uuid
from core.database import safe_execute

class ForumTopic:
    @staticmethod
    def create(user_id: int, title: str, content: str, category: str = "General") -> str:
        topic_id = f"TOP-{uuid.uuid4().hex[:8].upper()}"
        safe_execute("""
            INSERT INTO forum_topics (topic_id, user_id, title, content, category, status)
            VALUES (?, ?, ?, ?, ?, 'open')
        """, (topic_id, user_id, title, content, category))
        return topic_id

    @staticmethod
    def get_all(limit: int = 10, offset: int = 0, status: str = 'open'):
        if status == 'all':
            return safe_execute("""
                SELECT id, topic_id, user_id, title, category, status, created_at
                FROM forum_topics
                ORDER BY id DESC LIMIT ? OFFSET ?
            """, (limit, offset), fetch=True)
        return safe_execute("""
            SELECT id, topic_id, user_id, title, category, status, created_at
            FROM forum_topics
            WHERE status = ?
            ORDER BY id DESC LIMIT ? OFFSET ?
        """, (status, limit, offset), fetch=True)

    @staticmethod
    def get_detail(topic_pk: int):
        topic = safe_execute("""
            SELECT t.id, t.topic_id, t.user_id, t.title, t.content, t.category, t.status, t.created_at, t.updated_at, u.full_name
            FROM forum_topics t
            LEFT JOIN users u ON t.user_id = u.telegram_id
            WHERE t.id = ?
        """, (topic_pk,), fetch=True)

        comments = safe_execute("""
            SELECT c.id, c.user_id, c.comment_text, c.created_at, u.full_name
            FROM forum_comments c
            LEFT JOIN users u ON c.user_id = u.telegram_id
            WHERE c.topic_id = ?
            ORDER BY c.id ASC
        """, (topic_pk,), fetch=True)

        return topic, comments

    @staticmethod
    def close(topic_pk: int):
        safe_execute("UPDATE forum_topics SET status = 'closed', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (topic_pk,))

    @staticmethod
    def reopen(topic_pk: int):
        safe_execute("UPDATE forum_topics SET status = 'open', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (topic_pk,))

    @staticmethod
    def delete(topic_pk: int):
        safe_execute("DELETE FROM forum_comments WHERE topic_id = ?", (topic_pk,))
        safe_execute("DELETE FROM forum_topics WHERE id = ?", (topic_pk,))


class ForumComment:
    @staticmethod
    def add(topic_pk: int, user_id: int, comment_text: str):
        safe_execute("""
            INSERT INTO forum_comments (topic_id, user_id, comment_text)
            VALUES (?, ?, ?)
        """, (topic_pk, user_id, comment_text))
