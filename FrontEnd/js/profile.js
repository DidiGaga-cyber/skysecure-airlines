const { createApp } = Vue;

createApp({
    data() {
        return {
            userName: '',
            userSurname: '',
            userEmail: ''
        }
    },
    computed: {
        // Создаем инициалы (например, JK для Jan Kowalski)
        userInitials() {
            return (this.userName.charAt(0) + this.userSurname.charAt(0)).toUpperCase();
        }
    },
    mounted() {
        // Проверяем авторизацию
        const isLoggedIn = localStorage.getItem('isLoggedIn');
        if (!isLoggedIn) {
            window.location.href = 'login.html';
            return;
        }

        // Загружаем данные из localStorage
        this.userName = localStorage.getItem('userName') || 'Pasażer';
        this.userSurname = localStorage.getItem('userSurname') || '';
        this.userEmail = localStorage.getItem('userEmail') || 'brak@email.com';
    },
    methods: {
        goToHome() {
            window.location.href = 'index.html';
        },
        logout() {
            localStorage.clear();
            window.location.href = 'index.html';
        }
    }
}).mount('#app');