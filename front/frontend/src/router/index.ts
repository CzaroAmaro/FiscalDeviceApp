import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { isPublic: true }
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/devices',
      name: 'devices',
      component: () => import('../views/DevicesListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { isPublic: true }
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
  else {
    next()
  }
})


export default router
