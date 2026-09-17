from core.database import safe_execute

class Payment:
    @staticmethod
    def create(user_id: int, proof_file_id: str, amount: str | None = None):
        safe_execute("""
            INSERT INTO payments (user_id, proof_file_id, amount, status)
            VALUES (?, ?, ?, 'pending')
        """, (user_id, proof_file_id, amount))

    @staticmethod
    def verify(payment_id: int, admin_notes: str = "Verified by admin"):
        safe_execute("""
            UPDATE payments
            SET status = 'verified', admin_notes = ?
            WHERE id = ?
        """, (admin_notes, payment_id))

    @staticmethod
    def get_pending(limit: int = 20):
        return safe_execute("""
            SELECT id, user_id, proof_file_id, amount, status, created_at
            FROM payments
            WHERE status = 'pending'
            ORDER BY id ASC LIMIT ?
        """, (limit,), fetch=True)
