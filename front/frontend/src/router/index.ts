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
          meta: { requiresActivation: true },
        },
        {
          path: 'chart',
          name: 'chart',
          component: () => import('@/views/ChartView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'clients',
          name: 'client-list',
          component: () => import('../views/ClientsListView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'clients-map',
          name: 'client-map',
          component: () => import('../views/ClientsMapView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'devices',
          name: 'device-list',
          component: () => import('../views/DevicesListView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'manufacturers',
          name: 'manufacturer-list',
          component: () => import('../views/ManufacturerListView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'technicians',
          name: 'technician-list',
          component: () => import('../views/TechnicianListView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'tickets',
          name: 'ticket-list',
          component: () => import('../views/TicketListView.vue'),
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
        {
          path: 'certifications',
          name: 'certification-list',
          component: () => import('@/views/CertificationsView.vue'),
          meta: { requiresAdmin: true },
        },
        {
          path: 'chat',
          name: 'chat',
          component: () => import('@/views/ChatView.vue'),
        },
        {
          path: '/reports',
          name: 'reports',
          component: () => import('../views/ReportsView.vue'),
          meta: { requiresAdmin: true },
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
    {
      path: '/settings/confirm-email-change',
      name: 'confirm-email-change',
      component: () => import('@/views/ConfirmEmailChangeView.vue'),
      meta: { isPublic: true },
    },
    {
      path: '/unauthorized',
      name: 'unauthorized',
      component: () => import('../views/UnauthorizedView.vue'),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  const isAuthRoute = to.name === 'login' || to.name === 'register';

  if (isAuthenticated && isAuthRoute) {
    return next({ name: 'home' });
  }

  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } });
  }

  // Sprawdź uprawnienia admina
  if (to.meta.requiresAdmin) {
    // Upewnij się, że dane użytkownika są załadowane
    if (!authStore.user && isAuthenticated) {
      await authStore.fetchUser();
    }

    if (!authStore.isAdmin) {
      return next({ name: 'unauthorized' });
    }
  }

  next();
});

export default router
