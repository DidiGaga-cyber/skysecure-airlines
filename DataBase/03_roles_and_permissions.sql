-- Database roles and permissions

-- 1. Roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user_role') THEN
        CREATE ROLE app_user_role NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_admin_role') THEN
        CREATE ROLE app_admin_role NOLOGIN;
    END IF;
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_readonly_role') THEN
        CREATE ROLE app_readonly_role NOLOGIN;
    END IF;
END
$$;

-- 2. Permissions for app_user_role
GRANT SELECT ON loty, lotniska TO app_user_role;
GRANT UPDATE ON loty TO app_user_role;
GRANT SELECT, UPDATE ON miejsca TO app_user_role;
GRANT SELECT, INSERT, UPDATE ON rezerwacje TO app_user_role;
GRANT SELECT, INSERT ON bilety TO app_user_role;
GRANT SELECT, INSERT ON platnosci TO app_user_role;
GRANT SELECT, UPDATE ON uzytkownicy TO app_user_role;
GRANT SELECT, INSERT ON logi_audytowe TO app_user_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user_role;

-- 3. Permissions for app_admin_role
GRANT app_user_role TO app_admin_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO app_admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO app_admin_role;

-- 4. Permissions for app_readonly_role
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly_role;

-- 5. Row Level Security (RLS)
ALTER TABLE rezerwacje ENABLE ROW LEVEL SECURITY;
ALTER TABLE bilety     ENABLE ROW LEVEL SECURITY;
ALTER TABLE platnosci  ENABLE ROW LEVEL SECURITY;

ALTER TABLE rezerwacje FORCE ROW LEVEL SECURITY;
ALTER TABLE bilety     FORCE ROW LEVEL SECURITY;
ALTER TABLE platnosci  FORCE ROW LEVEL SECURITY;

-- Policies: rezerwacje
CREATE POLICY user_sees_own_reservations ON rezerwacje FOR SELECT TO app_user_role
    USING (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

CREATE POLICY user_inserts_own_reservations ON rezerwacje FOR INSERT TO app_user_role
    WITH CHECK (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

CREATE POLICY user_updates_own_reservations ON rezerwacje FOR UPDATE TO app_user_role
    USING (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

CREATE POLICY admin_sees_all_reservations ON rezerwacje FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- Policies: bilety
CREATE POLICY user_sees_own_tickets ON bilety FOR SELECT TO app_user_role
    USING (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY user_inserts_own_tickets ON bilety FOR INSERT TO app_user_role
    WITH CHECK (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY admin_sees_all_tickets ON bilety FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- Policies: platnosci
CREATE POLICY user_sees_own_payments ON platnosci FOR SELECT TO app_user_role
    USING (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY user_inserts_own_payments ON platnosci FOR INSERT TO app_user_role
    WITH CHECK (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY admin_sees_all_payments ON platnosci FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- 6. Role protection trigger
ALTER TABLE uzytkownicy ADD CONSTRAINT chk_rola_dozwolone_wartosci CHECK (rola IN ('User', 'Admin', 'Moderator'));

CREATE OR REPLACE FUNCTION fn_protect_rola_change()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.rola = 'Admin' AND OLD.rola <> 'Admin' THEN
        IF current_setting('app.current_user_role', TRUE) <> 'Admin' THEN
            RAISE EXCEPTION 'SECURITY VIOLATION: Brak uprawnień do nadania roli Admin.'
                USING ERRCODE = '42501';
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_protect_rola_change
    BEFORE UPDATE OF rola ON uzytkownicy
    FOR EACH ROW
    EXECUTE FUNCTION fn_protect_rola_change();

-- 7. Role grant
GRANT app_admin_role TO skysecure_user;
