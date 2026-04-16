const { createApp } = Vue;

createApp({
    data() {
        return {
            userName:    '',
            userSurname: '',
            userEmail:   '',
            bookings:    []
        };
    },
    computed: {
        userInitials() {
            return (this.userName.charAt(0) + this.userSurname.charAt(0)).toUpperCase();
        },
        // Liczba zrealizowanych (opłaconych) lotów
        flightCount() {
            return this.bookings.filter(b => b.status === 'Success' || b.status === 'Opłacona').length;
        }
    },
    mounted() {
        if (!localStorage.getItem('isLoggedIn')) {
            window.location.href = 'login.html';
            return;
        }
        this.userName    = localStorage.getItem('userName')    || 'Pasażer';
        this.userSurname = localStorage.getItem('userSurname') || '';
        this.userEmail   = localStorage.getItem('userEmail')   || 'brak@email.com';

        // Wczytaj rezerwacje z localStorage (zapisywane przez index.js po udanej płatności)
        const raw = localStorage.getItem('myBookings');
        this.bookings = raw ? JSON.parse(raw) : [];
    },
    methods: {
        goToHome() {
            window.location.href = 'index.html';
        },
        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        },
        formatDate(isoStr) {
            if (!isoStr) return '—';
            return new Date(isoStr).toLocaleString('pl-PL', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        },
        formatFlightDate(isoStr) {
            if (!isoStr) return '—';
            return new Date(isoStr).toLocaleString('pl-PL', {
                day: '2-digit', month: '2-digit', year: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        },
        formatPrice(val) {
            return parseFloat(val).toLocaleString('pl-PL', { minimumFractionDigits: 2 });
        },
        getStatusClass(status) {
            if (status === 'Success' || status === 'Opłacona')
                return 'bg-emerald-100 text-emerald-700 border-emerald-200';
            if (status === 'Pending')
                return 'bg-amber-100 text-amber-700 border-amber-200';
            return 'bg-red-100 text-red-700 border-red-200';
        },
        getStatusLabel(status) {
            const map = { Success: 'Opłacona', Pending: 'Oczekująca', Failed: 'Błąd' };
            return map[status] || status;
        },
        getMethodIcon(metoda) {
            const map = {
                'Karta':    '💳',
                'BLIK':     '📱',
                'ApplePay': ''
            };
            return map[metoda] || '💰';
        }
    }
}).mount('#app');