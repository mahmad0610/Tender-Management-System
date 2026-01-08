const API_URL = ""; // Relative path

const api = {
    login: async (username, password) => {
        const res = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (!res.ok) throw new Error('Login failed');
        return await res.json();
    },

    getTenders: async () => {
        const res = await fetch(`${API_URL}/tenders/`);
        return await res.json();
    },

    createTender: async (data) => {
        const res = await fetch(`${API_URL}/tenders/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    createContract: async (data) => {
        const res = await fetch(`${API_URL}/contracts/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    createPO: async (data) => {
        const res = await fetch(`${API_URL}/purchase_orders/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    getInvoices: async () => {
        const res = await fetch(`${API_URL}/invoices/`);
        return await res.json();
    },

    getContracts: async () => {
        const res = await fetch(`${API_URL}/contracts/`);
        return await res.json();
    },

    getPOs: async () => {
        const res = await fetch(`${API_URL}/purchase_orders/`);
        return await res.json();
    },

    getPayments: async () => {
        const res = await fetch(`${API_URL}/payments/`);
        return await res.json();
    },

    createPayment: async (data) => {
        const res = await fetch(`${API_URL}/payments/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    getMilestones: async (tenderId) => {
        const res = await fetch(`${API_URL}/tenders/${tenderId}/milestones`);
        return await res.json();
    },

    updateMilestone: async (mid, data) => {
        const res = await fetch(`${API_URL}/milestones/${mid}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },

    register: async (data) => {
        const res = await fetch(`${API_URL}/register/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(await res.text());
        return await res.json();
    },

    upload: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${API_URL}/upload/`, { method: 'POST', body: formData });
        if (!res.ok) {
            const err = await res.text();
            throw new Error(`Upload failed (${res.status}): ${err}`);
        }
        return await res.json();
    },

    getItems: async () => {
        const res = await fetch(`${API_URL}/items/`);
        if (!res.ok) throw new Error("Could not fetch items");
        return await res.json();
    },

    createItem: async (data) => {
        const res = await fetch(`${API_URL}/items/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error("Could not create item");
        return await res.json();
    }
};
