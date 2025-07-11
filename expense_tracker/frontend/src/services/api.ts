import axios, { type AxiosResponse } from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
    baseURL: `${API_BASE_URL}/api`,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
    }
})

// SỬA interceptor request
api.interceptors.request.use(async (config) => {
    if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
        try {
            const csrfResponse = await axios.get(`${API_BASE_URL}/api/csrf/`, {
                withCredentials: true
            })
            const csrfToken = csrfResponse.data.csrfToken
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken
            }
        } catch (error) {
            console.log('Could not get CSRF token:', error)
        }
    }
    return config
})

export const authApi = {
    login: (username: string, password: string) => {
        return api.post('/login/', { username, password })
    },
    logout: () => api.post('/logout/'),
    user: () => api.get('/user/'),
}

export const membersApi = {
    getAll: () => api.get('/members/'),
    create: (data: any) => api.post('/members/', data),
    update: (id: number, data: any) => api.put(`/members/${id}/`, data),
    delete: (id: number) => api.delete(`/members/${id}/`)
}

export const expensesApi = {
    getAll: () => api.get('/expenses/'),
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
        api.post('/telegram/send-bulk-reminders/', { member_ids: memberIds })
}

export default api