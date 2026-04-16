export const API_URL = 'http://127.0.0.1/api';

export const getAuthToken = () => localStorage.getItem('token');export const getUserEmail    = () => localStorage.getItem('userEmail');

export const setSession = (token, email) => {
    localStorage.setItem('token', token);
    localStorage.setItem('userEmail', email);
};

export const clearSession = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    // Дополнительные ключи, которые пишет login.js и profile.js
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('userEmail');
    localStorage.removeItem('userName');
    localStorage.removeItem('userSurname');
};