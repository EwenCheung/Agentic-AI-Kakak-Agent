// This file will contain the API calls to the backend.

const API_URL = 'http://localhost:8000';

export const sendMessage = async (message) => {
    const response = await fetch(`${API_URL}/message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message),
    });
    return response.json();
};

export const get = async (endpoint) => {
    const response = await fetch(`${API_URL}${endpoint}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

export const put = async (endpoint, data = {}) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

export const deleteRequest = async (endpoint) => {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

// Ticket specific API functions
export const toggleTicketStatus = async (ticketId) => {
    return await put(`/dashboard/tickets/${ticketId}/toggle-status`);
};

export const deleteTicket = async (ticketId) => {
    return await deleteRequest(`/dashboard/tickets/${ticketId}`);
};

export const getAllTickets = async () => {
    return await get('/dashboard/tickets/all');
};
