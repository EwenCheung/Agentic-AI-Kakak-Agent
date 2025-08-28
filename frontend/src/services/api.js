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
