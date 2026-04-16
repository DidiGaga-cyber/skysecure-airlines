import { API_URL, getAuthToken, getUserEmail, clearSession } from './state.js';

const { createApp, ref, reactive, computed } = Vue;

// ── НАСТРОЙКА AXIOS (ИНТЕРЦЕПТОР) ──────────────────────────────────────────
// Это гарантирует, что ПЕРЕД каждым запросом будет взят актуальный токен
axios.interceptors.request.use(config => {
    const token = getAuthToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});

createApp({
    setup() {
        const isLoggedIn = ref(!!getAuthToken());
        const userEmail  = ref(getUserEmail());

        const logout = () => {
            clearSession();
            window.location.reload();
        };

        // ... (поиск рейсов остается как был) ...
        const searchForm = reactive({ from: '', to: '', date: '' });
        const flights    = ref([]);
        const hasSearched = ref(false);
        const isLoading   = ref(false);

        const searchFlights = async () => {
            isLoading.value = true;
            hasSearched.value = true;
            try {
                const params = {};
                if (searchForm.from) params.from = searchForm.from;
                if (searchForm.to)   params.to   = searchForm.to;
                if (searchForm.date) params.date  = searchForm.date;
                const response = await axios.get(`${API_URL}/flights/`, { params });
                flights.value = response.data;
            } catch (error) {
                console.error("Błąd wyszukiwania:", error);
            } finally {
                isLoading.value = false;
            }
        };

        // ── БРОНИРОВАНИЕ ──────────────────────────────────────────────────────
        const activeFlightId = ref(null);
        const selectedSeat = ref(null);
        const passenger = reactive({ imie: '', nazwisko: '' });
        const seats = ref([]);
        const isBookingLoading = ref(false);

        const groupedSeats = computed(() => {
            const groups = {};
            seats.value.forEach(seat => {
                const match = seat.numer_miejsca.match(/(\d+)([A-Z]+)/);
                const row = match ? match[1] : 'Inne';
                if (!groups[row]) groups[row] = [];
                groups[row].push(seat);
            });
            return Object.keys(groups).sort((a,b) => parseInt(a)-parseInt(b)).map(row => ({
                row,
                seats: groups[row].sort((a,b) => a.numer_miejsca.localeCompare(b.numer_miejsca))
            }));
        });

        const startBooking = async (id) => {
            if (!isLoggedIn.value) {
                alert("Musisz się zalogować!");
                window.location.href = 'login.html';
                return;
            }
            activeFlightId.value = id;
            try {
                const response = await axios.get(`${API_URL}/flights/${id}/seats`);
                seats.value = response.data;
            } catch (error) {
                alert("Nie udało się załadować miejsc.");
            }
        };

        // ИСПРАВЛЕННЫЙ SUBMIT BOOKING
        const submitBooking = async () => {
            const token = getAuthToken();
            
            // Проверка 1: Есть ли токен вообще?
            if (!token) {
                alert("Błąd autoryzacji: Brak tokena. Zaloguj się ponownie.");
                window.location.href = 'login.html';
                return;
            }

            if (!passenger.imie || !passenger.nazwisko || !selectedSeat.value) {
                alert("Wypełnij wszystkie pola!");
                return;
            }

            isBookingLoading.value = true;
            
            try {
                console.log("Wysyłanie rezerwacji z tokenem:", token); // Для отладки

                // ШАГ 1: Создание реzerwacji
                // Благодаря интерцептору выше, заголовок Authorization добавится сам
                const resBooking = await axios.post(`${API_URL}/bookings/`, {
                    id_lotu: activeFlightId.value
                });
                
                const id_rezerwacji = resBooking.data.id_rezerwacji;

                // ШАГ 2: Создание билета
                await axios.post(`${API_URL}/tickets/`, {
                    id_rezerwacji: id_rezerwacji,
                    id_miejsca: selectedSeat.value.id_miejsca,
                    imie: passenger.imie,
                    nazwisko: passenger.nazwisko
                });

                alert(`Sukces! Zarezerwowano miejsce ${selectedSeat.value.numer_miejsca}`);
                resetView();
                searchFlights();
            } catch (error) {
                console.error("Детали ошибки 401:", error.response);
                if (error.response?.status === 401) {
                    alert("Sesja wygasła. Zaloguj się ponownie.");
                    logout(); // Очищаем всё и на логин
                } else {
                    alert("Błąd: " + (error.response?.data?.detail || "Serwer nie odpowiada"));
                }
            } finally {
                isBookingLoading.value = false;
            }
        };

        const resetView = () => {
            activeFlightId.value = null;
            selectedSeat.value = null;
            seats.value = [];
            passenger.imie = '';
            passenger.nazwisko = '';
        };

        const selectSeat = (seat) => { if (seat.czy_wolne) selectedSeat.value = seat; };
        const getSeatClass = (seat) => {
            if (selectedSeat.value?.id_miejsca === seat.id_miejsca) return 'seat-selected';
            return seat.czy_wolne ? 'seat-available' : 'seat-occupied';
        };

        const formatTime = (d) => new Date(d).toLocaleString('pl-PL', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
        const formatPrice = (p) => parseFloat(p).toLocaleString('pl-PL', { minimumFractionDigits: 2 });

        return {
            isLoggedIn, userEmail, logout,
            searchForm, searchFlights, flights, hasSearched, isLoading,
            activeFlightId, startBooking, resetView,
            seats, selectSeat, getSeatClass, selectedSeat,
            passenger, submitBooking, isBookingLoading, groupedSeats,
            formatTime, formatPrice
        };
    }
}).mount('#app');