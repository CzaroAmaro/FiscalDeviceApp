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
          path: '', // Domyślna ścieżka dla '/'
          name: 'home',
          component: () => import('../views/HomeView.vue'),
        },
        {
          path: 'clients',
          name: 'client-list', // <-- TA NAZWA MUSI PASOWAĆ DO MENU
          component: () => import('../views/ClientsListView.vue'),
        },
        {
          path: 'devices',
          name: 'device-list', // <-- TA NAZWA MUSI PASOWAĆ DO MENU
          component: () => import('../views/DevicesListView.vue'),
        },
        {
          path: 'manufacturers',
          name: 'manufacturer-list',
          component: () => import('../views/ManufacturerListView.vue'),
        },
      ],
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

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } });
  } else if (isAuthenticated && to.meta.isPublic) {
    next({ name: 'home' });
  } else {
    next();
  }
});

export default router
