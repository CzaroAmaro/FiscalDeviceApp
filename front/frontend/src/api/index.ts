import axios from "axios";


const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

// Interceptor do odpowiedzi API - kluczowy element!
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Jeśli serwer zwrócił błąd
    if (error.response && error.response.status === 401) {
      console.warn("Błąd 401 - Unauthorized. Wylogowywanie...");

      const { useAuthStore } = await import('@/stores/auth');
      const authStore = useAuthStore();

      authStore.logout();
    }
    return Promise.reject(error);
  }
);

api.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth');
  const authStore = useAuthStore();
  const token = authStore.accessToken;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});


export default api;
