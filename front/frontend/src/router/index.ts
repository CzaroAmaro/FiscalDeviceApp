import { createRouter, createWebHistory } from 'vue-router';

import DefaultLayout from '@/components/layout/Default.vue';
import { useAuthStore } from '@/stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { isPublic: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { isPublic: true },
    },

    {
      path: '/',
      component: DefaultLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'home',
          component: () => import('../views/HomeView.vue'),
        },
        {
          path: 'clients',
          name: 'client-list',
          component: () => import('../views/ClientsListView.vue'),
        },
        {
          path: 'devices',
          name: 'device-list',
          component: () => import('../views/DevicesListView.vue'),
        },
        {
          path: 'manufacturers',
          name: 'manufacturer-list',
          component: () => import('../views/ManufacturerListView.vue'),
        },
        {
          path: 'technicians',
          name: 'technician-list',
          component: () => import('../views/TechnicianListView.vue'),
        },
        {
          path: 'tickets',
          name: 'ticket-list',
          component: () => import('../views/TicketListView.vue'),
        },
        {
          path: 'purchase',
          name: 'purchase',
          component: () => import('@/views/PurchaseView.vue'),
        },
        {
          path: 'redeem',
          name: 'redeem-code',
          component: () => import('@/views/RedeemCodeView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/SettingsView.vue'),
        },
      ],
    },
    {
      path: '/payment/success',
      name: 'payment-success',
      component: () => import('@/views/PaymentSuccessView.vue'),
      meta: { isPublic: true }
    },
    {
      path: '/payment/cancel',
      name: 'payment-cancel',
      component: () => import('@/views/PaymentCancelView.vue'),
      meta: { isPublic: true }
    },

    // Ścieżka "catch-all" dla 404
    // {
    //   path: '/:pathMatch(.*)*',
    //   name: 'not-found',
    //   component: () => import('../views/NotFoundView.vue'), // Warto stworzyć taki widok
    // },
  ],
});

// === Ulepszony Strażnik Nawigacji ===
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  const isAuthRoute = to.name === 'login' || to.name === 'register';

  // 1. Jeśli użytkownik jest zalogowany i próbuje wejść na stronę logowania/rejestracji
  if (isAuthenticated && isAuthRoute) {
    return next({ name: 'home' });
  }
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }
  next();
});

export default router
