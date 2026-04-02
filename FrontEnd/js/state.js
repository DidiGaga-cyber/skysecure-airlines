export const API_URL = 'http://127.0.0.1/api'; 

export const getAuthToken = () => localStorage.getItem('skysecure_token');
export const getUserEmail = () => localStorage.getItem('skysecure_user_email');

export const setSession = (token, email) => {
    localStorage.setItem('skysecure_token', token);
    localStorage.setItem('skysecure_user_email', email);
};

export const clearSession = () => {
    localStorage.removeItem('skysecure_token');
    localStorage.removeItem('skysecure_user_email');
};