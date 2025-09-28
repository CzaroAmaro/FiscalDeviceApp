import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      // Dodajemy metadane, aby wiedzieć, że to strona logowania
      meta: { isPublic: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true } // Ta strona wymaga zalogowania
    },
    {
      path: '/devices',
      name: 'devices',
      component: () => import('../views/DevicesListView.vue'),
      meta: { requiresAuth: true } // Ta strona również wymaga zalogowania
    }
  ]
})

// --- Tu zaczyna się magia: STRAŻNIK NAWIGACJI ---
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated

  // Jeśli strona wymaga autoryzacji i użytkownik NIE jest zalogowany
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Przekieruj na stronę logowania
    next({ name: 'login' })
  }
  // Jeśli użytkownik jest zalogowany i próbuje wejść na stronę logowania
  else if (isAuthenticated && to.meta.isPublic) {
    // Przekieruj go na stronę główną
    next({ name: 'home' })
  }
  // W każdym innym przypadku, po prostu pozwól na nawigację
  else {
    next()
  }
})


export default router
