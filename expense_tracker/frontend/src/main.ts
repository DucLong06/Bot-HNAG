import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import App from './App.vue'
import router from './router'

// Vuetify styles and icons
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

// Vuetify theme configuration
const vuetify = createVuetify({
    components,
    directives,
    theme: {
        defaultTheme: 'light',
        themes: {
            light: {
                dark: false,
                colors: {
                    // Primary brand colors
                    primary: '#667eea',
                    'primary-darken-1': '#5a67d8',
                    'primary-lighten-1': '#7c8df0',

                    // Secondary colors
                    secondary: '#764ba2',
                    'secondary-darken-1': '#6b46c1',
                    'secondary-lighten-1': '#8b5fb8',

                    // Accent and utility colors
                    accent: '#667eea',
                    error: '#ff6b6b',
                    'error-darken-1': '#f05252',
                    info: '#4ecdc4',
                    'info-darken-1': '#06b6d4',
                    success: '#51cf66',
                    'success-darken-1': '#4caf50',
                    warning: '#ffd43b',
                    'warning-darken-1': '#ffc107',

                    // Surface colors
                    background: '#f8fafc',
                    surface: '#ffffff',
                    'surface-bright': '#ffffff',
                    'surface-light': '#f1f5f9',
                    'surface-variant': '#e2e8f0',
                    'on-surface-variant': '#475569',

                    // Text colors
                    'on-background': '#1f2937',
                    'on-surface': '#1f2937',
                    'on-primary': '#ffffff',
                    'on-secondary': '#ffffff',
                    'on-error': '#ffffff',
                    'on-info': '#ffffff',
                    'on-success': '#ffffff',
                    'on-warning': '#1f2937',

                    // Custom gradient colors
                    'gradient-1': '#667eea',
                    'gradient-2': '#764ba2',

                    // Card and elevation colors
                    'card-shadow': 'rgba(99, 102, 241, 0.08)',
                    'elevation-1': 'rgba(99, 102, 241, 0.05)',
                    'elevation-2': 'rgba(99, 102, 241, 0.08)',
                    'elevation-3': 'rgba(99, 102, 241, 0.12)',
                }
            },
            dark: {
                dark: true,
                colors: {
                    // Primary brand colors (adjusted for dark theme)
                    primary: '#818cf8',
                    'primary-darken-1': '#6366f1',
                    'primary-lighten-1': '#a5b4fc',

                    // Secondary colors
                    secondary: '#a78bfa',
                    'secondary-darken-1': '#8b5cf6',
                    'secondary-lighten-1': '#c4b5fd',

                    // Accent and utility colors
                    accent: '#818cf8',
                    error: '#f87171',
                    'error-darken-1': '#ef4444',
                    info: '#06b6d4',
                    'info-darken-1': '#0891b2',
                    success: '#34d399',
                    'success-darken-1': '#10b981',
                    warning: '#fbbf24',
                    'warning-darken-1': '#f59e0b',

                    // Surface colors (dark theme)
                    background: '#0f172a',
                    surface: '#1e293b',
                    'surface-bright': '#334155',
                    'surface-light': '#475569',
                    'surface-variant': '#64748b',
                    'on-surface-variant': '#cbd5e1',

                    // Text colors (dark theme)
                    'on-background': '#f1f5f9',
                    'on-surface': '#f1f5f9',
                    'on-primary': '#1e293b',
                    'on-secondary': '#1e293b',
                    'on-error': '#ffffff',
                    'on-info': '#ffffff',
                    'on-success': '#ffffff',
                    'on-warning': '#1e293b',

                    // Custom gradient colors (dark theme)
                    'gradient-1': '#818cf8',
                    'gradient-2': '#a78bfa'
                }
            }
        }
    },
    defaults: {
        // Global component defaults for consistent styling
        VCard: {
            elevation: 0,
            rounded: 'lg',
            class: 'modern-card'
        },
        VBtn: {
            style: 'text-transform: none; font-weight: 500; letter-spacing: 0;',
            rounded: 'lg'
        },
        VTextField: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
            hideDetails: 'auto'
        },
        VSelect: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
            hideDetails: 'auto'
        },
        VAutocomplete: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
            hideDetails: 'auto'
        },
        VTextarea: {
            variant: 'outlined',
            density: 'comfortable',
            rounded: 'lg',
            hideDetails: 'auto'
        },
        VDialog: {
            rounded: 'xl',
            scrollable: true
        },
        VChip: {
            rounded: 'lg'
        },
        VAlert: {
            rounded: 'lg',
            variant: 'tonal'
        },
        VSnackbar: {
            rounded: 'lg'
        },
        VProgressLinear: {
            rounded: true,
            height: 8
        },
        VProgressCircular: {
            size: 32,
            width: 3
        },
        VDataTable: {
            density: 'comfortable',
            rounded: 'lg'
        },
        VMenu: {
            rounded: 'lg'
        },
        VList: {
            rounded: 'lg'
        },
        VListItem: {
            rounded: 'lg'
        },
        VNavigationDrawer: {
            rounded: 'lg'
        },
        VTabs: {
            rounded: 'lg'
        },
        VTab: {
            rounded: 'lg'
        }
    },
    display: {
        mobileBreakpoint: 'sm',
        thresholds: {
            xs: 0,
            sm: 600,
            md: 960,
            lg: 1280,
            xl: 1920,
        },
    }
})

// Create Vue app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)
app.use(vuetify)

// Global error handler
app.config.errorHandler = (err, instance, info) => {
    console.error('Global error:', err)
    console.error('Component info:', info)
}

// Global properties (if needed)
app.config.globalProperties.$appName = 'Expense Tracker'
app.config.globalProperties.$version = '1.0.0'

// Mount app
app.mount('#app')