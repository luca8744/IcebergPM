const API_URL = '/api';

const auth = {
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || 'Login failed');
        }

        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({
            username: data.username,
            role: data.role
        }));
        return data;
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    },

    getToken() {
        return localStorage.getItem('token');
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    async fetch(url, options = {}) {
        const token = this.getToken();
        const headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };

        const response = await fetch(`${API_URL}${url}`, { ...options, headers });
        
        if (response.status === 401) {
            this.logout();
            return;
        }
        
        return response;
    },

    async getVersion() {
        const response = await fetch(`${API_URL}/version`);
        if (!response.ok) return '0.0.0';
        const data = await response.json();
        return data.version;
    }
};
