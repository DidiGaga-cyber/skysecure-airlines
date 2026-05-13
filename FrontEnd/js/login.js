import { API_URL, setSession } from './state.js';

const { createApp, ref } = Vue;

createApp({
    setup() {
        const isRegisterMode = ref(false);
        const form = ref({ email: '', password: '', imie: '', nazwisko: '' });

        const goToHome = () => {
            window.location.href = 'index.html';
        };

        const handleAuth = async () => {
            if (isRegisterMode.value) {
                // ── REJESTRACJA ──────────────────────────────────────────────
                try {
                    const payload = {
                        email:    form.value.email,
                        password: form.value.password,
                        imie:     form.value.imie,
                        nazwisko: form.value.nazwisko
                    };
                    await axios.post(`${API_URL}/auth/register`, payload);

                    localStorage.setItem('userName',    form.value.imie    || 'Pasażer');
                    localStorage.setItem('userSurname', form.value.nazwisko || '');

                    alert("Rejestracja udana! Możesz się teraz zalogować.");
                    isRegisterMode.value = false;
                } catch (e) {
                    alert("Błąd rejestracji:\n" + JSON.stringify(e.response?.data?.detail || e.message, null, 2));
                }

            } else {
                // ── LOGOWANIE ────────────────────────────────────────────────
                try {
                    const p = new URLSearchParams();
                    p.append('username', form.value.email);
                    p.append('password', form.value.password);

                    const r = await axios.post(`${API_URL}/auth/login`, p);

                    // Zapisujemy token i email
                    setSession(r.data.access_token, form.value.email);
                    localStorage.setItem('isLoggedIn', 'true');
                    localStorage.setItem('userEmail',  form.value.email);

                    if (form.value.imie) {
                        localStorage.setItem('userName',    form.value.imie);
                        localStorage.setItem('userSurname', form.value.nazwisko || '');
                    }

                    // ── SPRAWDZAMY ROLĘ Z TOKENA ─────────────────────────────
                    // JWT payload (środkowa część) to zwykły base64 — dekodujemy bez bibliotek
                    const payload = JSON.parse(atob(r.data.access_token.split('.')[1]));
                    const role = payload.role;

                    if (role === 'Admin') {
                        window.location.href = 'admin.html';
                    } else {
                        window.location.href = 'index.html';
                    }

                } catch (e) {
                    alert("Błąd logowania:\n" + JSON.stringify(e.response?.data?.detail || e.message, null, 2));
                }
            }
        };

        return { isRegisterMode, form, handleAuth, goToHome };
    }
}).mount('#app');