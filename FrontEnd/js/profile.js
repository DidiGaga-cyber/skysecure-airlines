const { createApp } = Vue;

createApp({
    data() {
        return {
            userName:    '',
            userSurname: '',
            userEmail:   '',
            bookings:    [],
            // Stan pobierania PDF per rezerwacja: { [id_bileta]: 'idle'|'loading'|'error' }
            pdfStates:   {}
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
        },
        async downloadTicketPdf(booking) {
            const id = booking.id_bileta;
            if (!id) {
                this.pdfStates = { ...this.pdfStates, [booking.id_rezerwacji]: 'error' };
                return;
            }
            const token = localStorage.getItem('token');
            if (!token) {
                window.location.href = 'login.html';
                return;
            }
            const key = id;
            this.pdfStates = { ...this.pdfStates, [key]: 'loading' };
            try {
                const res = await fetch(`https://localhost/api/tickets/${id}/pdf`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (!res.ok) {
                    throw new Error(res.status === 401
                        ? 'Brak autoryzacji'
                        : `Błąd ${res.status}`);
                }
                const blob = await res.blob();
                const url  = URL.createObjectURL(blob);
                const a    = document.createElement('a');
                a.href     = url;
                a.download = `ticket_${id}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                this.pdfStates = { ...this.pdfStates, [key]: 'idle' };
            } catch (err) {
                this.pdfStates = { ...this.pdfStates, [key]: 'error' };
                console.error('PDF download error:', err);
            }
        }
    }
}).mount('#app');