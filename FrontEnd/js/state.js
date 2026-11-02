export const API_URL = 'https://localhost/api';

export const getAuthToken  = () => localStorage.getItem('token');
export const getUserEmail  = () => localStorage.getItem('userEmail');

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

export const isTokenExpired = () => {
    const token = localStorage.getItem('token');
    if (!token) return true;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (!payload.exp) return true;
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

export const setupAxiosInterceptors = (onExpired) => {
    const defaultHandler = () => {
        clearSession();
        import('./notify.js').then(({ showToast }) => {
            showToast('Twoja sesja wygasła. Zaloguj się ponownie.', 'warning', 5000);
        });
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
    };

    const handleExpired = onExpired || defaultHandler;

    // Request interceptor: check expiration before request
    axios.interceptors.request.use(
        config => {
            const token = getAuthToken();
            if (token) {
                if (isTokenExpired()) {
                    handleExpired();
                    return Promise.reject(new axios.Cancel('Token expired'));
                }
                config.headers.Authorization = `Bearer ${token}`;
            }
            return config;
        },
        error => Promise.reject(error)
    );

    // Response interceptor: handle 401
    axios.interceptors.response.use(
        response => response,
        error => {
            if (error.response?.status === 401) {
                const isLoginPage = window.location.pathname.endsWith('login.html');
                if (!isLoginPage) {
                    handleExpired();
                }
            }
            return Promise.reject(error);
        }
    );
};
