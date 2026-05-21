export const API_URL = 'https://localhost/api';

export const getAuthToken  = () => localStorage.getItem('token');
export const getUserEmail  = () => localStorage.getItem('userEmail');

/**
 * Dekoduje payload z JWT i zwraca rolę użytkownika ('Admin' | 'User' | null).
 */
export const getUserRole = () => {
    const token = localStorage.getItem('token');
    if (!token) return null;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role || null;
    } catch {
        return null;
    }
};

/**
 * Sprawdza czy token JWT już wygasł.
 * Pole `exp` w JWT to timestamp w sekundach (Unix time).
 * Zwraca true jeśli token nie istnieje LUB już wygasł.
 */
export const isTokenExpired = () => {
    const token = localStorage.getItem('token');
    if (!token) return true;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (!payload.exp) return true;
        // payload.exp jest w sekundach, Date.now() w milisekundach
        return Date.now() >= payload.exp * 1000;
    } catch {
        return true;
    }
};

export const setSession = (token, email) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userEmail', email);
};

export const clearSession = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userName');
    localStorage.removeItem('userSurname');
};

/**
 * Konfiguruje globalne interceptory Axios do obsługi wygasania sesji JWT.
 *
 * - Request interceptor: sprawdza token PRZED każdym żądaniem.
 *   Jeśli token wygasł lokalnie → natychmiast wylogowuje, bez wysyłania żądania.
 *
 * - Response interceptor: łapie odpowiedź 401 z serwera.
 *   Jeśli serwer odrzuci token (np. wygasł tuż po sprawdzeniu) → wylogowuje.
 *
 * @param {Function} onExpired - callback wywoływany przy wykryciu wygaśnięcia.
 *   Domyślnie pokazuje toast i przekierowuje na login.html.
 *   Możesz nadpisać dla testów lub custom UX.
 */
export const setupAxiosInterceptors = (onExpired) => {
    const defaultHandler = () => {
        clearSession();
        // Importujemy dynamicznie żeby uniknąć circular dependency
        import('./notify.js').then(({ showToast }) => {
            showToast('Twoja sesja wygasła. Zaloguj się ponownie.', 'warning', 5000);
        });
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500); // małe opóźnienie żeby toast zdążył się pokazać
    };

    const handleExpired = onExpired || defaultHandler;

    // ── REQUEST INTERCEPTOR ──────────────────────────────────────────────────
    // Sprawdza exp lokalnie przed wysłaniem żądania — oszczędza round-trip do serwera
    axios.interceptors.request.use(
        config => {
            const token = getAuthToken();
            if (token) {
                if (isTokenExpired()) {
                    handleExpired();
                    // Anulujemy żądanie przez rzucenie błędu — axios nie wyśle requestu
                    return Promise.reject(new axios.Cancel('Token wygasł'));
                }
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        error => Promise.reject(error)
    );

    // ── RESPONSE INTERCEPTOR ─────────────────────────────────────────────────
    // Łapie 401 z serwera — np. token wygasł dokładnie między sprawdzeniem a odpowiedzią
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response?.status === 401) {
                // Upewniamy się że to naprawdę problem z tokenem, nie np. błędne dane logowania
                // Na stronie login.html nie chcemy pętli przekierowań
                const isLoginPage = window.location.pathname.endsWith('login.html');
                if (!isLoginPage) {
                    handleExpired();
                }
            }
            return Promise.reject(error);
        }
    );
};