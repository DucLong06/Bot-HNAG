import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
    history: createWebHistory('/'),
    routes: [
        {
            path: '/',
            name: 'home',
            component: () => import('../views/HomeView.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/members',
            name: 'members',
            component: () => import('../views/MembersView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/expenses',
            name: 'expenses',
            component: () => import('../views/ExpensesView.vue'),
            meta: { requiresAuth: true }
        },
        {
            path: '/expenses/:id',
            name: 'expense-detail',
            component: () => import('../views/ExpenseDetailView.vue'),
            props: true
        }
    ]
})

router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        // Try to check if user is already logged in
        const isAuthenticated = await authStore.checkAuth()

        if (!isAuthenticated) {
            next('/login')
        } else {
            next()
        }
    } else {
        next()
    }
})

export default router