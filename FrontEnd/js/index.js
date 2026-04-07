import { API_URL, getAuthToken, getUserEmail, clearSession } from './state.js';

const { createApp, ref, reactive, onMounted } = Vue;

createApp({
    setup() {
        // AUTORYZACJA
        const isLoggedIn = ref(!!getAuthToken());
        const userEmail = ref(getUserEmail());
        
        // Ustawienie tokena dla wszystkich zapytań Axios
        if (isLoggedIn.value) {
            axios.defaults.headers.common['Authorization'] = `Bearer ${getAuthToken()}`;
        }

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
                // Usuwamy puste pola, żeby nie wysyłać undefined/null do API
                const params = {};
                if (searchForm.from) params.from = searchForm.from;
                if (searchForm.to) params.to = searchForm.to;
                if (searchForm.date) params.date = searchForm.date;

                const response = await axios.get(`${API_URL}/flights/`, { params });
                flights.value = response.data;
            } catch (error) {
                console.error("Błąd API:", error);
            } finally {
                isLoading.value = false;
            }
        };

        // REZERWACJA (Sprint 4)
        const activeFlightId = ref(null);
        const selectedSeat = ref(null);
        // Dodano pole paszport (wymagane przez backend)
        const passenger = reactive({ imie: '', nazwisko: '', paszport: '' });
        
        // Zaktualizowana struktura pod bazę danych
        // Gdy Backend doda endpoint GET /flights/{id}/miejsca, po prostu zrobisz przypisanie do tej zmiennej
        const seats = ref([
            { id_miejsca: 1, numer_miejsca: '1A', klasa: 'Business', czy_wolne: false },
            { id_miejsca: 2, numer_miejsca: '1B', klasa: 'Business', czy_wolne: true },
            { id_miejsca: 3, numer_miejsca: '12A', klasa: 'Economy', czy_wolne: false },
            { id_miejsca: 4, numer_miejsca: '12B', klasa: 'Economy', czy_wolne: true },
            { id_miejsca: 5, numer_miejsca: '14A', klasa: 'Economy', czy_wolne: true },
            { id_miejsca: 6, numer_miejsca: '14B', klasa: 'Economy', czy_wolne: true }
        ]);

        const startBooking = (id_lotu) => {
            if (!isLoggedIn.value) {
                alert("Musisz się zalogować, aby zarezerwować bilet.");
                window.location.href = 'login.html';
                return;
            }
            activeFlightId.value = id_lotu;
            // Tutaj w przyszłości: seats.value = await axios.get(`${API_URL}/flights/${id_lotu}/miejsca`)
        };

        const resetView = () => { 
            activeFlightId.value = null; 
            selectedSeat.value = null; 
            passenger.imie = '';
            passenger.nazwisko = '';
            passenger.paszport = '';
        };

        const selectSeat = (seat) => { 
            if (seat.czy_wolne) selectedSeat.value = seat; 
        };
        
        const getSeatClass = (seat) => {
            if (selectedSeat.value?.id_miejsca === seat.id_miejsca) return 'seat-selected';
            return seat.czy_wolne ? 'seat-available' : 'seat-occupied';
        };

        const submitBooking = async () => {
            if (passenger.imie && passenger.nazwisko && passenger.paszport && selectedSeat.value) {
                try {
                    // Krok 1: Tworzymy rezerwację (blokuje miejsce na lot w kolumnie liczba_miejsc)
                    const bookingResponse = await axios.post(`${API_URL}/bookings/`, {
                        id_lotu: activeFlightId.value
                    });
                    
                    const id_rezerwacji = bookingResponse.data.id_rezerwacji;

                    // Krok 2: Wystawiamy bilet na konkretne miejsce z szyfrowaniem paszportu
                    await axios.post(`${API_URL}/tickets/`, {
                        id_rezerwacji: id_rezerwacji,
                        id_miejsca: selectedSeat.value.id_miejsca,
                        imie: passenger.imie,
                        nazwisko: passenger.nazwisko,
                        paszport: passenger.paszport
                    });

                    alert(`Sukces! Zarezerwowano miejsce ${selectedSeat.value.numer_miejsca}. Dane paszportowe zostały zaszyfrowane (AES-256).`);
                    resetView();
                    // Opcjonalnie: odśwież listę lotów
                    searchFlights();
                } catch (error) {
                    console.error(error);
                    alert("Błąd podczas rezerwacji: " + (error.response?.data?.detail || error.message));
                }
            } else {
                alert("Wypełnij wszystkie dane i wybierz miejsce.");
            }
        };

        // POMOCNICZE FORMATERY
        const formatTime = (d) => new Date(d).toLocaleString('pl-PL', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
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