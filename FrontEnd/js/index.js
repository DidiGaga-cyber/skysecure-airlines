import { API_URL, getAuthToken, getUserEmail, clearSession } from './state.js';
import { showToast } from './notify.js';
const { createApp, ref, reactive, computed } = Vue;

// ── AXIOS INTERCEPTOR ────────────────────────────────────────────────────────
axios.interceptors.request.use(config => {
    const token = getAuthToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
}, error => Promise.reject(error));

createApp({
    setup() {
        // ── AUTH ─────────────────────────────────────────────────────────────
        const isLoggedIn = ref(!!getAuthToken());
        const userEmail  = ref(getUserEmail());
        const logout = () => { clearSession(); window.location.reload(); };

        // ── WIDOK: 'search' | 'booking' | 'payment' | 'success' ─────────────
        const currentView = ref('search');

        // ── WYSZUKIWANIE ─────────────────────────────────────────────────────
        const searchForm  = reactive({ from: '', to: '', date: '' });
        const flights     = ref([]);
        const hasSearched = ref(false);
        const isLoading   = ref(false);

        // Кэш аэропортов: { [id]: объект аэропорта }
        const airportCache = {};
        const fetchAirport = async (id) => {
            if (!id) return null;
            if (airportCache[id]) return airportCache[id];
            try {
                const res = await axios.get(`${API_URL}/flights/airports/${id}`);
                airportCache[id] = res.data;
                return res.data;
            } catch { return null; }
        };

        const searchFlights = async () => {
            isLoading.value   = true;
            hasSearched.value = true;
            try {
                const params = {};
                if (searchForm.from) params.from = searchForm.from;
                if (searchForm.to)   params.to   = searchForm.to;
                if (searchForm.date) params.date  = searchForm.date;
                const response = await axios.get(`${API_URL}/flights/`, { params });
                const rawFlights = response.data;

                // Загружаем все уникальные аэропорты параллельно
                const uniqueIds = [...new Set(rawFlights.flatMap(f => [f.id_lotniska_odlotu, f.id_lotniska_przylotu]).filter(Boolean))];
                await Promise.all(uniqueIds.map(fetchAirport));

                // Обогащаем каждый рейс данными аэропортов
                flights.value = rawFlights.map(f => ({
                    ...f,
                    lotnisko_skad:  airportCache[f.id_lotniska_odlotu]  || null,
                    lotnisko_dokad: airportCache[f.id_lotniska_przylotu] || null,
                }));
            } catch (error) {
                console.error("Błąd wyszukiwania:", error);
            } finally {
                isLoading.value = false;
            }
        };

        // ── REZERWACJA ───────────────────────────────────────────────────────
        const activeFlightId    = ref(null);
        const currentFlight     = ref(null);
        const selectedSeat      = ref(null);
        const passenger         = reactive({ imie: '', nazwisko: '' });
        const seats             = ref([]);
        const isBookingLoading  = ref(false);
        const hoverSeat         = ref(null);

        // Grupowanie miejsc według numerów rzędów
        const groupedSeats = computed(() => {
            const groups = {};
            seats.value.forEach(seat => {
                const match = seat.numer_miejsca.match(/^(\d+)([A-Z]+)$/);
                const row   = match ? match[1] : 'Inne';
                if (!groups[row]) groups[row] = [];
                groups[row].push(seat);
            });
            return Object.keys(groups)
                .sort((a, b) => parseInt(a) - parseInt(b))
                .map(row => ({
                    row,
                    left:  groups[row].filter(s => /[ABC]$/.test(s.numer_miejsca)).sort((a,b) => a.numer_miejsca.localeCompare(b.numer_miejsca)),
                    right: groups[row].filter(s => /[DEF]$/.test(s.numer_miejsca)).sort((a,b) => a.numer_miejsca.localeCompare(b.numer_miejsca)),
                    all:   groups[row].sort((a,b) => a.numer_miejsca.localeCompare(b.numer_miejsca))
                }));
        });

        const startBooking = async (id) => {
            if (!isLoggedIn.value) {
                showToast("Musisz się zalogować!");
                window.location.href = 'login.html';
                return;
            }
            activeFlightId.value = id;
            currentFlight.value  = flights.value.find(f => f.id_lotu === id) || null;
            currentView.value    = 'booking';
            try {
                const response = await axios.get(`${API_URL}/flights/${id}/seats`);
                seats.value = response.data;
            } catch (error) {
                showToast("Nie udało się załadować mapy miejsc.");
            }
        };

        // Dane rezerwacji przekazywane do ekranu płatności
        const reservationData = reactive({ id_rezerwacji: null, kwota: 0 });

        // ID biletu zwracane przez POST /tickets/ – potrzebne do pobrania PDF
        const ticketId = ref(null);

        const submitBooking = async () => {
            const token = getAuthToken();
            if (!token) {
                showToast("Błąd autoryzacji: Brak tokena. Zaloguj się ponownie.");
                window.location.href = 'login.html';
                return;
            }
            if (!passenger.imie || !passenger.nazwisko || !selectedSeat.value) {
                showToast("Wypełnij wszystkie pola i wybierz miejsce!", 'warning');
                return;
            }
            isBookingLoading.value = true;
            try {
                // Krok 1: Utwórz rezerwację
                const resBooking = await axios.post(`${API_URL}/bookings/`, {
                    id_lotu: activeFlightId.value
                });
                const id_rezerwacji = resBooking.data.id_rezerwacji;

                // Krok 2: Utwórz bilet – zapisz id_bileta do stanu
                const resTicket = await axios.post(`${API_URL}/tickets/`, {
                    id_rezerwacji,
                    id_miejsca: selectedSeat.value.id_miejsca,
                    imie:       passenger.imie,
                    nazwisko:   passenger.nazwisko
                });
                ticketId.value = resTicket.data.id_bileta ?? null;

                // Przejście do ekranu płatności
                reservationData.id_rezerwacji = id_rezerwacji;
                reservationData.kwota         = parseFloat(currentFlight.value?.cena || 0);
                currentView.value = 'payment';
            } catch (error) {
                if (error.response?.status === 401) {
                    showToast("Sesja wygasła. Zaloguj się ponownie.");
                    logout();
                } else {
                    showToast("Błąd: " + (error.response?.data?.detail || "Serwer nie odpowiada"));
                }
            } finally {
                isBookingLoading.value = false;
            }
        };

        // ── PŁATNOŚĆ ─────────────────────────────────────────────────────────
        const paymentMethod    = ref('Karta');
        const cardDetails      = reactive({ number: '', expiry: '', cvc: '', name: '' });
        const blikCode         = ref('');
        const isPaymentLoading = ref(false);
        const successData      = reactive({
            id_platnosci: null, identyfikator_sesji: null, kwota: 0, metoda: ''
        });

        // Auto-formatowanie numeru karty: "4111 1111 1111 1111"
        const onCardNumberInput = (e) => {
            let raw = e.target.value.replace(/\D/g, '').slice(0, 16);
            cardDetails.number = raw.replace(/(.{4})/g, '$1 ').trim();
        };
        const onExpiryInput = (e) => {
            let raw = e.target.value.replace(/\D/g, '').slice(0, 4);
            if (raw.length >= 3) raw = raw.slice(0,2) + '/' + raw.slice(2);
            cardDetails.expiry = raw;
        };

        const processPayment = async () => {
            if (paymentMethod.value === 'Karta') {
                if (!cardDetails.number || !cardDetails.expiry || !cardDetails.cvc || !cardDetails.name) {
                    showToast("Wypełnij wszystkie dane karty!", "warning");
                    return;
                }
            }
            if (paymentMethod.value === 'BLIK') {
                if (blikCode.value.replace(/\D/g,'').length !== 6) {
                    showToast("Wprowadź poprawny 6-cyfrowy kod BLIK!", "warning");
                    return;
                }
            }
            isPaymentLoading.value = true;
            try {
                const res = await axios.post(`${API_URL}/payments/process`, {
                    id_rezerwacji: reservationData.id_rezerwacji,
                    metoda: paymentMethod.value
                });
                successData.id_platnosci       = res.data.id_platnosci;
                successData.identyfikator_sesji = res.data.identyfikator_sesji;
                successData.kwota              = res.data.kwota;
                successData.metoda             = res.data.metoda;

                // Zapisz do localStorage → profil
                _saveBookingToStorage(res.data);
                currentView.value = 'success';
            } catch (error) {
                if (error.response?.status === 401) {
                    showToast("Sesja wygasła. Zaloguj się ponownie.");
                    logout();
                } else {
                    showToast("Błąd płatności: " + (error.response?.data?.detail || "Serwer nie odpowiada"));
                }
            } finally {
                isPaymentLoading.value = false;
            }
        };

        const _saveBookingToStorage = (paymentResult) => {
            const existing = JSON.parse(localStorage.getItem('myBookings') || '[]');
            existing.unshift({
                id_rezerwacji:       reservationData.id_rezerwacji,
                id_platnosci:        paymentResult.id_platnosci,
                id_bileta:           ticketId.value,
                numer_lotu:          currentFlight.value?.numer_lotu  || '—',
                seat:                selectedSeat.value?.numer_miejsca || '—',
                klasa:               selectedSeat.value?.klasa         || '—',
                pasazer:             `${passenger.imie} ${passenger.nazwisko}`,
                kwota:               paymentResult.kwota,
                status:              paymentResult.status_transakcji,
                metoda:              paymentResult.metoda,
                identyfikator_sesji: paymentResult.identyfikator_sesji,
                czas_odlotu:         currentFlight.value?.czas_odlotu  || null,
                data_zakupu:         new Date().toISOString()
            });
            localStorage.setItem('myBookings', JSON.stringify(existing));
        };

        // ── POBIERANIE PDF BILETU ─────────────────────────────────────────────
        const isPdfLoading  = ref(false);
        const pdfError      = ref('');

        const downloadTicketPdf = async () => {
            if (!ticketId.value) {
                pdfError.value = 'Brak identyfikatora biletu.';
                return;
            }
            const token = getAuthToken();
            if (!token) {
                showToast("Sesja wygasła. Zaloguj się ponownie.");
                logout();
                return;
            }
            isPdfLoading.value = true;
            pdfError.value     = '';
            try {
                const res = await fetch(`${API_URL}/tickets/${ticketId.value}/pdf`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (!res.ok) {
                    const msg = res.status === 401
                        ? 'Brak autoryzacji – zaloguj się ponownie.'
                        : `Nie udało się pobrać PDF (błąd ${res.status}).`;
                    throw new Error(msg);
                }
                const blob = await res.blob();
                const url  = URL.createObjectURL(blob);
                const a    = document.createElement('a');
                a.href     = url;
                a.download = `ticket_${ticketId.value}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            } catch (err) {
                pdfError.value = err.message || 'Wystąpił błąd podczas pobierania biletu.';
            } finally {
                isPdfLoading.value = false;
            }
        };


        const resetView = () => {
            currentView.value         = 'search';
            activeFlightId.value      = null;
            currentFlight.value       = null;
            selectedSeat.value        = null;
            seats.value               = [];
            passenger.imie            = '';
            passenger.nazwisko        = '';
            reservationData.id_rezerwacji = null;
            reservationData.kwota     = 0;
            cardDetails.number        = '';
            cardDetails.expiry        = '';
            cardDetails.cvc           = '';
            cardDetails.name          = '';
            blikCode.value            = '';
            hoverSeat.value           = null;
            ticketId.value            = null;
            isPdfLoading.value        = false;
            pdfError.value            = '';
        };

        // ── STYLE MIEJSC (inline, niezależne od Tailwind) ────────────────────
        const selectSeat = (seat) => { if (seat.czy_wolne) selectedSeat.value = seat; };

        const getSeatStyle = (seat) => {
            const isSelected = selectedSeat.value?.id_miejsca === seat.id_miejsca;
            const isHov      = hoverSeat.value === seat.id_miejsca && seat.czy_wolne;
            const isBusiness = seat.klasa === 'Business';

            if (isSelected) return {
                backgroundColor: '#2563eb', borderColor: '#1d4ed8',
                color: '#fff', transform: 'scale(1.12)',
                boxShadow: '0 0 22px rgba(37,99,235,0.50)', cursor: 'pointer'
            };
            if (!seat.czy_wolne) return {
                backgroundColor: '#f1f5f9', borderColor: '#e2e8f0',
                color: '#cbd5e1', textDecoration: 'line-through', cursor: 'not-allowed'
            };
            if (isBusiness) return {
                backgroundColor: isHov ? '#fffbeb' : '#fff',
                borderColor:     isHov ? '#f59e0b' : '#fde68a',
                color:           isHov ? '#92400e' : '#b45309',
                transform:       isHov ? 'scale(1.1)' : 'scale(1)',
                boxShadow:       isHov ? '0 8px 18px rgba(245,158,11,0.25)' : 'none',
                cursor: 'pointer', transition: 'all 0.15s ease'
            };
            return {
                backgroundColor: isHov ? '#eff6ff' : '#fff',
                borderColor:     isHov ? '#3b82f6' : '#e2e8f0',
                color:           isHov ? '#2563eb' : '#64748b',
                transform:       isHov ? 'scale(1.1)' : 'scale(1)',
                boxShadow:       isHov ? '0 8px 18px rgba(59,130,246,0.20)' : 'none',
                cursor: 'pointer', transition: 'all 0.15s ease'
            };
        };

        // ── FORMATOWANIE ─────────────────────────────────────────────────────
        const formatTime  = (d) => new Date(d).toLocaleString('pl-PL', { day:'2-digit', month:'2-digit', hour:'2-digit', minute:'2-digit' });
        const formatPrice = (p) => parseFloat(p).toLocaleString('pl-PL', { minimumFractionDigits: 2 });
        const formatDate  = (d) => d ? new Date(d).toLocaleDateString('pl-PL') : '—';

        return {
            isLoggedIn, userEmail, logout,
            currentView, resetView,
            searchForm, searchFlights, flights, hasSearched, isLoading,
            activeFlightId, currentFlight, startBooking,
            seats, selectSeat, getSeatStyle, selectedSeat, hoverSeat, groupedSeats,
            passenger, submitBooking, isBookingLoading,
            reservationData,
            paymentMethod, cardDetails, blikCode,
            isPaymentLoading, processPayment, onCardNumberInput, onExpiryInput,
            successData,
            ticketId, isPdfLoading, pdfError, downloadTicketPdf,
            formatTime, formatPrice, formatDate
        };
    }
}).mount('#app');