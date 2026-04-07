import { API_URL, getAuthToken, getUserEmail, clearSession } from './state.js';

const { createApp, ref, computed, onMounted } = Vue;

createApp({
    setup() {
        const isLoggedIn = ref(!!getAuthToken());
        const userEmail = ref(getUserEmail());
        
        // Zabezpieczenie trasy
        if (!isLoggedIn.value) {
            window.location.href = 'login.html';
        }

        if (isLoggedIn.value) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${getAuthToken()}`;
        }

        const logout = () => { 
            clearSession(); 
            window.location.href = 'index.html'; 
        };

        const activeTab = ref('active'); // 'active' lub 'history'
        const isLoading = ref(true);
        const tickets = ref([]);

        // Dane użytkownika - mockowane do momentu powstania GET /users/me
        const userData = ref({
            imie: 'Jan', // Docelowo z bazy
            nazwisko: 'Kowalski',
            rola: 'User',
            data_rejestracji: '2026-04-01'
        });

        // Pobieranie danych
        const fetchProfileData = async () => {
            isLoading.value = true;
            try {
                // TODO: Odkomentować, gdy backend przygotuje endpointy
                // const userResp = await axios.get(`${API_URL}/users/me`);
                // userData.value = userResp.data;
                
                // const ticketsResp = await axios.get(`${API_URL}/tickets/me`);
                // tickets.value = ticketsResp.data;

                // MOCK DANYCH: Symulacja odpowiedzi z połączonych tabel bazy danych
                setTimeout(() => {
                    tickets.value = [
                        {
                            id_biletu: 1,
                            numer_lotu: 'SK1001',
                            odlot_iata: 'WAW',
                            odlot_miasto: 'Warszawa',
                            przylot_iata: 'JFK',
                            przylot_miasto: 'Nowy Jork',
                            czas_odlotu: '2026-05-10T10:00:00',
                            czas_przylotu: '2026-05-10T14:30:00',
                            cena: 2500.00,
                            numer_miejsca: '12A',
                            klasa: 'Economy',
                            imie_pasazera: 'Jan',
                            nazwisko_pasazera: 'Kowalski',
                            status: 'Opłacona' // z rezerwacji
                        },
                        {
                            id_biletu: 2,
                            numer_lotu: 'SK1003',
                            odlot_iata: 'WAW',
                            odlot_miasto: 'Warszawa',
                            przylot_iata: 'CDG',
                            przylot_miasto: 'Paryż',
                            czas_odlotu: '2025-12-15T08:00:00', // Przeszły lot
                            czas_przylotu: '2025-12-15T10:15:00',
                            cena: 600.00,
                            numer_miejsca: '4C',
                            klasa: 'Economy',
                            imie_pasazera: 'Jan',
                            nazwisko_pasazera: 'Kowalski',
                            status: 'Zakończona'
                        }
                    ];
                    isLoading.value = false;
                }, 800);

            } catch (error) {
                console.error("Błąd pobierania profilu:", error);
                isLoading.value = false;
            }
        };

        onMounted(() => {
            fetchProfileData();
        });

        // Filtrowanie biletów (Aktywne vs Historia)
        const filteredTickets = computed(() => {
            const now = new Date();
            if (activeTab.value === 'active') {
                return tickets.value.filter(t => new Date(t.czas_odlotu) >= now);
            } else {
                return tickets.value.filter(t => new Date(t.czas_odlotu) < now);
            }
        });

        // Pomocnicze funkcje UI
        const formatDateTime = (dateString) => {
            return new Date(dateString).toLocaleString('pl-PL', { 
                day: '2-digit', month: 'short', year: 'numeric', 
                hour: '2-digit', minute: '2-digit' 
            });
        };

        const formatPrice = (p) => parseFloat(p).toLocaleString('pl-PL', { minimumFractionDigits: 2 });

        const getStatusClass = (status) => {
            switch(status) {
                case 'Opłacona': return 'bg-green-100 text-green-700';
                case 'Oczekująca': return 'bg-amber-100 text-amber-700';
                case 'Zakończona': return 'bg-slate-200 text-slate-600';
                case 'Anulowana': return 'bg-red-100 text-red-700';
                default: return 'bg-blue-100 text-blue-700';
            }
        };

        return {
            isLoggedIn, userEmail, logout,
            userData, tickets, isLoading, activeTab, filteredTickets,
            formatDateTime, formatPrice, getStatusClass
        };
    }
}).mount('#app');