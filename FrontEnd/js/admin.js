
import { API_URL, getAuthToken, getUserRole, clearSession } from './state.js';


const { createApp, ref, onMounted } = Vue;

// Axios Interceptor dla JWT [cite: 122]
axios.interceptors.request.use(config => {
    const token = getAuthToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
}, error => Promise.reject(error));

createApp({
    setup() {
        const flights = ref([]);
        const isLoading = ref(false);

        // --- ZARZĄDZANIE FORMULARZEM ---
        const showModal = ref(false);
        const isEditing = ref(false);
        const currentFlightId = ref(null);
        
        const defaultForm = {
            numer_lotu: '', id_lotniska_odlotu: '', id_lotniska_przylotu: '',
            czas_odlotu: '', czas_przylotu: '', cena: '', liczba_miejsc: '', status: 'Zaplanowany'
        };
        const flightForm = ref({ ...defaultForm });

        const formatForInput = (isoString) => {
            if (!isoString) return '';
            // Konwertuje datę na format akceptowany przez <input type="datetime-local">
            return new Date(isoString).toISOString().slice(0, 16);
        };

        const checkAuth = () => {
            if (!getAuthToken()) {
                window.location.href = 'login.html';
                return;
            }
            if (getUserRole() !== 'Admin') {
                alert('Brak uprawnień. Ta strona jest tylko dla administratorów.');
                window.location.href = 'login.html';
            }
        };

        const loadFlights = async () => {
            isLoading.value = true;
            try {
                const response = await axios.get(`${API_URL}/flights/`);
                flights.value = response.data;
            } catch (error) {
                console.error("Błąd pobierania lotów:", error);
            } finally {
                isLoading.value = false;
            }
        };

        const openAddModal = () => {
            isEditing.value = false;
            currentFlightId.value = null;
            flightForm.value = { ...defaultForm };
            showModal.value = true;
        };

        const openEditModal = (flight) => {
            isEditing.value = true;
            currentFlightId.value = flight.id_lotu;
            flightForm.value = {
                numer_lotu: flight.numer_lotu,
                id_lotniska_odlotu: flight.id_lotniska_odlotu,
                id_lotniska_przylotu: flight.id_lotniska_przylotu,
                czas_odlotu: formatForInput(flight.czas_odlotu),
                czas_przylotu: formatForInput(flight.czas_przylotu),
                cena: flight.cena,
                liczba_miejsc: flight.liczba_miejsc,
                status: flight.status
            };
            showModal.value = true;
        };

        const saveFlight = async () => {
            try {
                // Przekształcamy typy danych zgodnie ze schematami Pydantic w backendzie
                const payload = {
                    ...flightForm.value,
                    id_lotniska_odlotu: parseInt(flightForm.value.id_lotniska_odlotu),
                    id_lotniska_przylotu: parseInt(flightForm.value.id_lotniska_przylotu),
                    cena: parseFloat(flightForm.value.cena),
                    liczba_miejsc: parseInt(flightForm.value.liczba_miejsc)
                };

                if (isEditing.value) {
                    await axios.put(`${API_URL}/flights/${currentFlightId.value}`, payload);
                } else {
                    await axios.post(`${API_URL}/flights/`, payload);
                }
                
                showModal.value = false;
                loadFlights(); // Odśwież widok tabeli po udanej akcji
            } catch (error) {
                if (error.response?.status === 403) {
                    alert("Brak uprawnień. Zaloguj się jako Admin.");
                } else if (error.response?.status === 409 || error.response?.status === 404 || error.response?.status === 400) {
                    alert("Błąd: " + error.response.data.detail);
                } else {
                    alert("Wystąpił błąd podczas zapisywania lotu.");
                }
            }
        };

        const deleteFlight = async (id_lotu) => {
            if (!confirm("OSTRZEŻENIE: Czy na pewno chcesz usunąć ten lot? Spowoduje to usunięcie powiązanych miejsc i rezerwacji (CASCADE)[cite: 31].")) {
                return;
            }

            try {
                await axios.delete(`${API_URL}/flights/${id_lotu}`);
                loadFlights();
            } catch (error) {
                if (error.response?.status === 403) {
                    alert("Błąd: Brak uprawnień! Tylko konto z rolą Admin może usuwać loty[cite: 31, 32].");
                } else if (error.response?.status === 409) {
                    alert("Błąd: " + error.response.data.detail);
                } else {
                    alert("Błąd serwera przy usuwaniu lotu.");
                }
            }
        };

        const logout = () => {
            clearSession();
            window.location.href = 'login.html';
        };

        const formatTime = (d) => new Date(d).toLocaleString('pl-PL', { 
            day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' 
        });

        onMounted(() => {
            checkAuth();
            loadFlights();
        });

        return {
            flights, isLoading, showModal, isEditing, flightForm,
            openAddModal, openEditModal, saveFlight, deleteFlight, 
            logout, formatTime
        };
    }
}).mount('#app');
