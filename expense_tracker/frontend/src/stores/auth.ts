import { defineStore } from 'pinia'
import { authApi } from '../services/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        isAuthenticated: false,
        user: null as any,
        loading: false
    }),

    actions: {
        async login(username: string, password: string) {
            this.loading = true
            try {
                const response = await authApi.login(username, password)
                this.isAuthenticated = true
                this.user = response.data
                return true
            } catch (error: any) {
                console.error('Login error:', error)
                this.isAuthenticated = false
                this.user = null
                return false
            } finally {
                this.loading = false
            }
        },

        async logout() {
            this.loading = true
            try {
                await authApi.logout()
            } catch (error) {
                console.error('Logout error:', error)
            } finally {
                this.isAuthenticated = false
                this.user = null
                this.loading = false
            }
        },

        async checkAuth() {
            try {
                const response = await authApi.user()
                this.isAuthenticated = true
                this.user = response.data
                return true
            } catch (error) {
                this.isAuthenticated = false
                this.user = null
                return false
            }
        }
    }
})