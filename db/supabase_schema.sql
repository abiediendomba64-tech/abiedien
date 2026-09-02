-- ============================================================
-- Enterprise Support Bot - Supabase PostgreSQL baseline schema
-- Architecture: backend/service-role only
-- Run this file in Supabase SQL Editor for a fresh database.
-- Application RBAC is enforced in the backend; the browser never
-- receives SUPABASE_SERVICE_ROLE_KEY.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255),
    email VARCHAR(255),
    phone_encrypted BYTEA,
    role VARCHAR(50) NOT NULL DEFAULT 'new_user',
    domain_name VARCHAR(255),
    domain_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verification_token VARCHAR(255),
    verification_expiry TIMESTAMPTZ,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT users_valid_role CHECK (
        role IN ('new_user', 'member', 'admin', 'dev', 'super_admin', 'root')
    ),
    CONSTRAINT users_valid_status CHECK (
        status IN ('active', 'suspended', 'banned')
    )
);

-- ============================================================
-- 2. TICKETS
-- ticket_number is generated from the same PostgreSQL sequence
-- used by id, avoiding COUNT(*) + 1 race conditions.
-- ============================================================
CREATE TABLE IF NOT EXISTS public.tickets (
    id BIGSERIAL PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    assigned_to BIGINT REFERENCES public.users(id) ON DELETE SET NULL,
    category VARCHAR(100) NOT NULL,
    priority VARCHAR(50) NOT NULL DEFAULT 'medium',
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    title VARCHAR(255),
    description TEXT,
    collected_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    resolution_notes TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT tickets_valid_priority CHECK (
        priority IN ('urgent', 'high', 'medium', 'low')
    ),
    CONSTRAINT tickets_valid_status CHECK (
        status IN ('draft', 'pending', 'assigned', 'waiting_member',
                   'in_progress', 'escalated', 'resolved', 'closed', 'rejected', 'cancelled')
    )
);

-- ============================================================
-- 3. TICKET MESSAGES
-- ============================================================
CREATE TABLE IF NOT EXISTS public.ticket_messages (
    id BIGSERIAL PRIMARY KEY,
    ticket_id BIGINT NOT NULL REFERENCES public.tickets(id) ON DELETE CASCADE,
    sender_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    sender_type VARCHAR(30) NOT NULL DEFAULT 'member',
    message TEXT NOT NULL,
    intent VARCHAR(100),
    confidence NUMERIC(5,4),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT ticket_messages_valid_sender_type CHECK (
        sender_type IN ('member', 'admin', 'dev', 'super_admin', 'root', 'system')
    ),
    CONSTRAINT ticket_messages_valid_confidence CHECK (
        confidence IS NULL OR (confidence >= 0 AND confidence <= 1)
    )
);

-- ============================================================
-- 4. CONVERSATION STATES
-- ============================================================
CREATE TABLE IF NOT EXISTS public.conversation_states (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    intent VARCHAR(100),
    active_ticket_id BIGINT REFERENCES public.tickets(id) ON DELETE SET NULL,
    last_topic VARCHAR(100),
    collected_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    waiting_for VARCHAR(100),
    state VARCHAR(50) NOT NULL DEFAULT 'idle',
    last_message_hash VARCHAR(128),
    last_interaction TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT conversation_states_valid_state CHECK (
        state IN ('idle', 'awaiting_domain', 'awaiting_reason', 'awaiting_amount',
                  'awaiting_confirmation', 'in_ticket', 'complete')
    )
);

-- ============================================================
-- 5. PAYMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.payments (
    id BIGSERIAL PRIMARY KEY,
    payment_number VARCHAR(20) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    amount NUMERIC(12,2) NOT NULL,
    payment_method VARCHAR(50),
    proof_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    verified_by BIGINT REFERENCES public.users(id) ON DELETE SET NULL,
    verification_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    verified_at TIMESTAMPTZ,

    CONSTRAINT payments_valid_amount CHECK (amount > 0),
    CONSTRAINT payments_valid_status CHECK (
        status IN ('pending', 'verified', 'rejected', 'cancelled')
    )
);

-- ============================================================
-- 6. FORUM TOPICS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.forum_topics (
    id BIGSERIAL PRIMARY KEY,
    topic_number VARCHAR(20) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL REFERENCES public.users(id) ON DELETE RESTRICT,
    category VARCHAR(100),
    title VARCHAR(255),
    description TEXT,
    is_locked BOOLEAN NOT NULL DEFAULT FALSE,
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- 7. AUDIT LOGS - IMMUTABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id BIGSERIAL PRIMARY KEY,
    actor_id BIGINT REFERENCES public.users(id) ON DELETE RESTRICT,
    actor_role VARCHAR(50),
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    reason TEXT,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- FUNCTIONS
-- ============================================================

CREATE OR REPLACE FUNCTION public.prevent_audit_log_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit_logs is immutable: % is not permitted', TG_OP;
END;
$$;

CREATE OR REPLACE FUNCTION public.set_ticket_number()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.id IS NULL THEN
        NEW.id := nextval(pg_get_serial_sequence('public.tickets', 'id'));
    END IF;

    IF NEW.ticket_number IS NULL OR NEW.ticket_number = '' THEN
        NEW.ticket_number := 'TKT-' || NEW.id::text;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.set_payment_number()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.id IS NULL THEN
        NEW.id := nextval(pg_get_serial_sequence('public.payments', 'id'));
    END IF;

    IF NEW.payment_number IS NULL OR NEW.payment_number = '' THEN
        NEW.payment_number := 'PAY-' || NEW.id::text;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.set_topic_number()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.id IS NULL THEN
        NEW.id := nextval(pg_get_serial_sequence('public.forum_topics', 'id'));
    END IF;

    IF NEW.topic_number IS NULL OR NEW.topic_number = '' THEN
        NEW.topic_number := 'TOP-' || NEW.id::text;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$;

-- ============================================================
-- IDEMPOTENT TRIGGERS
-- ============================================================

DROP TRIGGER IF EXISTS audit_logs_immutable ON public.audit_logs;
CREATE TRIGGER audit_logs_immutable
BEFORE UPDATE OR DELETE ON public.audit_logs
FOR EACH ROW
EXECUTE FUNCTION public.prevent_audit_log_mutation();

DROP TRIGGER IF EXISTS tickets_set_number ON public.tickets;
CREATE TRIGGER tickets_set_number
BEFORE INSERT ON public.tickets
FOR EACH ROW
EXECUTE FUNCTION public.set_ticket_number();

DROP TRIGGER IF EXISTS payments_set_number ON public.payments;
CREATE TRIGGER payments_set_number
BEFORE INSERT ON public.payments
FOR EACH ROW
EXECUTE FUNCTION public.set_payment_number();

DROP TRIGGER IF EXISTS forum_topics_set_number ON public.forum_topics;
CREATE TRIGGER forum_topics_set_number
BEFORE INSERT ON public.forum_topics
FOR EACH ROW
EXECUTE FUNCTION public.set_topic_number();

DROP TRIGGER IF EXISTS users_set_updated_at ON public.users;
CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS tickets_set_updated_at ON public.tickets;
CREATE TRIGGER tickets_set_updated_at
BEFORE UPDATE ON public.tickets
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS conversation_states_set_updated_at ON public.conversation_states;
CREATE TRIGGER conversation_states_set_updated_at
BEFORE UPDATE ON public.conversation_states
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

DROP TRIGGER IF EXISTS forum_topics_set_updated_at ON public.forum_topics;
CREATE TRIGGER forum_topics_set_updated_at
BEFORE UPDATE ON public.forum_topics
FOR EACH ROW
EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON public.users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON public.users(role);
CREATE INDEX IF NOT EXISTS idx_users_status ON public.users(status);
CREATE INDEX IF NOT EXISTS idx_tickets_user_id ON public.tickets(user_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON public.tickets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON public.tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON public.tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON public.tickets(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_ticket_id ON public.ticket_messages(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_messages_created_at ON public.ticket_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversation_states_user_id ON public.conversation_states(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON public.payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON public.payments(status);
CREATE INDEX IF NOT EXISTS idx_forum_topics_user_id ON public.forum_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_actor_id ON public.audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- ============================================================
-- ROW LEVEL SECURITY
-- Backend uses service_role. No anon/authenticated client access
-- is granted to application tables by this baseline.
-- ============================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticket_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversation_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forum_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Explicit deny-all policies for client roles.
-- service_role bypasses RLS and is the only production application path.
DROP POLICY IF EXISTS users_deny_anon ON public.users;
CREATE POLICY users_deny_anon ON public.users
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS users_deny_authenticated ON public.users;
CREATE POLICY users_deny_authenticated ON public.users
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS tickets_deny_anon ON public.tickets;
CREATE POLICY tickets_deny_anon ON public.tickets
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS tickets_deny_authenticated ON public.tickets;
CREATE POLICY tickets_deny_authenticated ON public.tickets
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS ticket_messages_deny_anon ON public.ticket_messages;
CREATE POLICY ticket_messages_deny_anon ON public.ticket_messages
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS ticket_messages_deny_authenticated ON public.ticket_messages;
CREATE POLICY ticket_messages_deny_authenticated ON public.ticket_messages
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS conversation_states_deny_anon ON public.conversation_states;
CREATE POLICY conversation_states_deny_anon ON public.conversation_states
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS conversation_states_deny_authenticated ON public.conversation_states;
CREATE POLICY conversation_states_deny_authenticated ON public.conversation_states
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS payments_deny_anon ON public.payments;
CREATE POLICY payments_deny_anon ON public.payments
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS payments_deny_authenticated ON public.payments;
CREATE POLICY payments_deny_authenticated ON public.payments
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS forum_topics_deny_anon ON public.forum_topics;
CREATE POLICY forum_topics_deny_anon ON public.forum_topics
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS forum_topics_deny_authenticated ON public.forum_topics;
CREATE POLICY forum_topics_deny_authenticated ON public.forum_topics
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS audit_logs_deny_anon ON public.audit_logs;
CREATE POLICY audit_logs_deny_anon ON public.audit_logs
AS RESTRICTIVE FOR ALL TO anon
USING (false) WITH CHECK (false);

DROP POLICY IF EXISTS audit_logs_deny_authenticated ON public.audit_logs;
CREATE POLICY audit_logs_deny_authenticated ON public.audit_logs
AS RESTRICTIVE FOR ALL TO authenticated
USING (false) WITH CHECK (false);

-- ============================================================
-- IMPORTANT
-- Do not grant SUPABASE_SERVICE_ROLE_KEY to the frontend.
-- Backend RBAC (@require_role / equivalent) remains authoritative.
-- ============================================================
