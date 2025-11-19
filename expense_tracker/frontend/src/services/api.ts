// Updated content for expense_tracker/frontend/src/services/api.ts

import axios, { type AxiosResponse } from 'axios'

const API_BASE_URL = '/api'

const api = axios.create({
    baseURL: `${API_BASE_URL}`,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
})

api.interceptors.request.use(async (config) => {
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {

        let csrfToken = getCookie('csrftoken')

        if (!csrfToken) {
            try {
                await axios.get(`${API_BASE_URL}/csrf/`, {
                    withCredentials: true
                })
                csrfToken = getCookie('csrftoken')
            } catch (error) {
                console.log('Could not get CSRF token:', error)
            }
        }

        if (csrfToken) {
            config.headers['X-CSRFToken'] = csrfToken
        }
    }
    return config
})

function getCookie(name: string) {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}

export const authApi = {
    getCsrfToken: () => axios.get(`${API_BASE_URL}/csrf/`, { withCredentials: true }),
    login: (username: string, password: string) => {
        return api.post('/login/', { username, password })
    },
    logout: () => api.post('/logout/'),
    user: () => api.get('/user/')
}

export const membersApi = {
    getAll: (search?: string) => api.get('/members/', { params: { search } }),
    create: (data: any) => api.post('/members/', data),
    update: (id: number, data: any) => api.put(`/members/${id}/`, data),
    delete: (id: number) => api.delete(`/members/${id}/`),
    getDebtSummary: (id: number) => api.get(`/members/${id}/debt_summary/`)
}

export const expensesApi = {
    getAll: (search?: string, payer?: number | null) =>
        api.get('/expenses/', { params: { search, payer } }),

    get: (id: number) => api.get(`/expenses/${id}/`),
    create: (data: any) => api.post('/expenses/', data),
    update: (id: number, data: any) => api.put(`/expenses/${id}/`, data),
    delete: (id: number) => api.delete(`/expenses/${id}/`),
    markPaid: (id: number, participantId: number) =>
        api.post(`/expenses/${id}/mark_paid/`, { participant_id: participantId })
}

export const telegramApi = {
    sendReminder: (memberId: number) =>
        api.post('/telegram/send-reminder/', { member_id: memberId }),
    sendBulkReminders: (memberIds: number[]) =>
        api.post('/telegram/send-bulk-reminders/', { member_ids: memberIds }),

    // NEW: API tập trung tạo QR Code
    generateQrCode: (data: { bank_name: string, account_number: string, amount: number, description: string, account_name: string }) =>
        api.post('/telegram/generate-qr/', data)
}

export default api