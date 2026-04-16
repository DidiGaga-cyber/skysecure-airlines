-- =============================================================================
-- 03_roles_and_permissions.sql
-- SkySecure Airlines — Role i Uprawnienia na poziomie bazy danych
-- =============================================================================

-- SEKCJA 1: ROLE POSTGRESQL
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

-- SEKCJA 2: UPRAWNIENIA DLA ROLI app_user_role (User)
-- Разрешаем чтение рейсов и аэропортов
GRANT SELECT ON loty, lotniska TO app_user_role;

-- ВАЖНО: Разрешаем обновлять таблицу loty (нужно для уменьшения количества мест при бронировании)
GRANT UPDATE ON loty TO app_user_role;

-- Разрешаем выбирать и занимать места
GRANT SELECT, UPDATE ON miejsca TO app_user_role;

-- Разрешаем работу с бронированиями, билетами и платежами
-- Добавлен UPDATE на rezerwacje для смены статусов
GRANT SELECT, INSERT, UPDATE ON rezerwacje TO app_user_role;
GRANT SELECT, INSERT ON bilety TO app_user_role;
GRANT SELECT, INSERT ON platnosci TO app_user_role;

-- Профиль пользователя и логи
GRANT SELECT, UPDATE ON uzytkownicy TO app_user_role;
GRANT SELECT, INSERT ON logi_audytowe TO app_user_role;

-- Права на все ID (последовательности)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user_role;



-- SEKCJA 3: UPRAWNIENIA DLA ROLI app_admin_role (Admin)
GRANT app_user_role TO app_admin_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_admin_role;

-- SEKCJA 4: UPRAWNIENIA DLA ROLI app_readonly_role
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly_role;

-- SEKCJA 5: ROW LEVEL SECURITY (RLS)
ALTER TABLE rezerwacje ENABLE ROW LEVEL SECURITY;
ALTER TABLE bilety     ENABLE ROW LEVEL SECURITY;
ALTER TABLE platnosci  ENABLE ROW LEVEL SECURITY;

ALTER TABLE rezerwacje FORCE ROW LEVEL SECURITY;
ALTER TABLE bilety     FORCE ROW LEVEL SECURITY;
ALTER TABLE platnosci  FORCE ROW LEVEL SECURITY;

-- --- Политики для REZERWACJI ---
CREATE POLICY user_sees_own_reservations ON rezerwacje FOR SELECT TO app_user_role
    USING (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

CREATE POLICY user_inserts_own_reservations ON rezerwacje FOR INSERT TO app_user_role
    WITH CHECK (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

-- НОВОЕ: Политика на обновление только своей брони
CREATE POLICY user_updates_own_reservations ON rezerwacje FOR UPDATE TO app_user_role
    USING (id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER);

CREATE POLICY admin_sees_all_reservations ON rezerwacje FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- --- Политики для BILETÓW ---
CREATE POLICY user_sees_own_tickets ON bilety FOR SELECT TO app_user_role
    USING (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY user_inserts_own_tickets ON bilety FOR INSERT TO app_user_role
    WITH CHECK (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY admin_sees_all_tickets ON bilety FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- --- Политики для PŁATNOŚCI ---
CREATE POLICY user_sees_own_payments ON platnosci FOR SELECT TO app_user_role
    USING (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY user_inserts_own_payments ON platnosci FOR INSERT TO app_user_role
    WITH CHECK (id_rezerwacji IN (SELECT id_rezerwacji FROM rezerwacje WHERE id_uzytkownika = current_setting('app.current_user_id', TRUE)::INTEGER));

CREATE POLICY admin_sees_all_payments ON platnosci FOR ALL TO app_admin_role USING (TRUE) WITH CHECK (TRUE);

-- SEKCJA 6: WALIDACJA ROLI 'Admin'
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

-- SEKCJA 7: PRZYPISANIE RÓL
GRANT app_admin_role TO skysecure_user;