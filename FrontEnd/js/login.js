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
                try {
                    const payload = {
                        email: form.value.email,
                        password: form.value.password, 
                        imie: form.value.imie,
                        nazwisko: form.value.nazwisko
                    };
                    await axios.post(`${API_URL}/auth/register`, payload);
                    alert("Rejestracja udana! Możesz się teraz zalogować.");
                    isRegisterMode.value = false;
                } catch (e) {
                    alert("Błąd rejestracji:\n" + JSON.stringify(e.response?.data?.detail || e.message, null, 2));
                }
            } else {
                try {
                    const p = new URLSearchParams();
                    p.append('username', form.value.email);
                    p.append('password', form.value.password);
                    const r = await axios.post(`${API_URL}/auth/login`, p);
                    
                    // Zapisujemy sesję i wracamy na stronę główną
                    setSession(r.data.access_token, form.value.email);
                    window.location.href = 'index.html';
                } catch (e) {
                    alert("Błąd logowania:\n" + JSON.stringify(e.response?.data?.detail || e.message, null, 2));
                }
            }
        };

        return { isRegisterMode, form, handleAuth, goToHome };
    }
}).mount('#app');