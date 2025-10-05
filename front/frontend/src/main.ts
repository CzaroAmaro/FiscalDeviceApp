import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import api from '@/api'
import {useAuthStore} from "@/stores/auth.ts";

import 'vuetify/styles'
import {createVuetify} from "vuetify";
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import {mdi} from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        sets: {
            mdi,
        },
    },
})

const token = localStorage.getItem('accessToken')
if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

const authStore = useAuthStore()
authStore.initialize()

app.mount('#app')
