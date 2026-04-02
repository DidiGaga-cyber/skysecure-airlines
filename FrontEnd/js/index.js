import { API_URL, getAuthToken, getUserEmail, clearSession } from './state.js';

const { createApp, ref, reactive } = Vue;

createApp({
    setup() {
        // AUTORYZACJA
        const isLoggedIn = ref(!!getAuthToken());
        const userEmail = ref(getUserEmail());
        
        const logout = () => { 
            clearSession(); 
            window.location.reload(); 
        };

        // WYSZUKIWANIE
        const searchForm = reactive({ from: '', to: '', date: '' });
        const flights = ref([]);
        const hasSearched = ref(false);
        const isLoading = ref(false);

        const searchFlights = async () => {
            isLoading.value = true; 
            hasSearched.value = true;
            try {
                const params = { ...searchForm };
                const response = await axios.get(`${API_URL}/flights/`, { params });
                flights.value = response.data;
            } catch (error) {
                console.error("Błąd API:", error);
            } finally {
                isLoading.value = false;
            }
        };

        // REZERWACJA
        const activeFlightId = ref(null);
        const selectedSeat = ref(null);
        const passenger = reactive({ imie: '', nazwisko: '' });
        
        // Mockowane miejsca (potem podłączysz pod API)
        const seats = ref([
            { id: 1, numer_miejsca: '1A', czy_wolne: false },
            { id: 2, numer_miejsca: '1B', czy_wolne: true },
            { id: 3, numer_miejsca: '12A', czy_wolne: false },
            { id: 4, numer_miejsca: '12B', czy_wolne: true },
            { id: 5, numer_miejsca: '14A', czy_wolne: true },
            { id: 6, numer_miejsca: '14B', czy_wolne: true }
        ]);

        const startBooking = (id) => {
            if (!isLoggedIn.value) {
                alert("Musisz się zalogować, aby zarezerwować bilet.");
                window.location.href = 'login.html';
                return;
            }
            activeFlightId.value = id;
        };

        const resetView = () => { 
            activeFlightId.value = null; 
            selectedSeat.value = null; 
            passenger.imie = '';
            passenger.nazwisko = '';
        };

        const selectSeat = (seat) => { 
            if (seat.czy_wolne) selectedSeat.value = seat; 
        };
        
        const getSeatClass = (seat) => {
            if (selectedSeat.value?.id === seat.id) return 'seat-selected';
            return seat.czy_wolne ? 'seat-available' : 'seat-occupied';
        };

        const submitBooking = () => {
            if (passenger.imie && passenger.nazwisko && selectedSeat.value) {
                // Tu w przyszłości będzie axios.post(...)
                alert(`Sukces! Zarezerwowano miejsce ${selectedSeat.value.numer_miejsca} dla: ${passenger.imie} ${passenger.nazwisko}`);
                resetView();
            }
        };

        // POMOCNICZE FORMATERY
        const formatTime = (d) => new Date(d).toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' });
        const formatPrice = (p) => parseFloat(p).toLocaleString('pl-PL', { minimumFractionDigits: 2 });

        return { 
            isLoggedIn, userEmail, logout, 
            searchForm, searchFlights, flights, hasSearched, isLoading, 
            activeFlightId, startBooking, resetView, seats, selectSeat, getSeatClass, selectedSeat, 
            passenger, submitBooking,
            formatTime, formatPrice
        };
    }
}).mount('#app');