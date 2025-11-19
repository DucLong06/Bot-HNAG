import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { fileURLToPath, URL } from 'node:url'

// https://vitejs.dev/config/
export default defineConfig({
    // [QUAN TRỌNG] Base url cho static files khi chạy qua Django
    base: '/static/',
    plugins: [
        vue(),
        vuetify({
            autoImport: true,
            theme: {
                defaultTheme: 'light'
            }
        })
    ],
    define: {
        'process.env': {},
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    css: {
        preprocessorOptions: {
            scss: {
                additionalData: `@import "@/assets/variables.scss";`
            }
        }
    },
    server: {
        port: 3000,
        host: true,
        open: true
    },
    build: {
        target: 'esnext',
        minify: 'esbuild',
        sourcemap: false,
        // Output directory configuration
        outDir: 'dist',
        assetsDir: 'assets',
        emptyOutDir: true,
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ['vue', 'vue-router', 'pinia'],
                    vuetify: ['vuetify']
                }
            }
        }
    },
    optimizeDeps: {
        include: ['vue', 'vue-router', 'pinia', 'vuetify', 'axios']
    }
})