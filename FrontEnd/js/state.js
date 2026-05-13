export const API_URL = 'https://localhost/api';

export const getAuthToken  = () => localStorage.getItem('token');
export const getUserEmail  = () => localStorage.getItem('userEmail');

/**
 * Dekoduje payload z JWT i zwraca rolę użytkownika ('Admin' | 'User' | null).
 * Nie wymaga żadnych zewnętrznych bibliotek — JWT payload to zwykły base64.
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