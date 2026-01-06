import axios from 'axios';

export function extractApiError(error: unknown, fallbackMessage: string = 'Wystąpił nieznany błąd'): string {
  if (!axios.isAxiosError(error)) {
    if (error instanceof Error) {
      return error.message;
    }
    return fallbackMessage;
  }

  const responseData = error.response?.data;

  if (responseData) {
    if (typeof responseData.message === 'string') {
      return responseData.message;
    }

    if (typeof responseData.detail === 'string') {
      return responseData.detail;
    }

    if (typeof responseData.error === 'string') {
      return responseData.error;
    }

    if (typeof responseData === 'string') {
      return responseData;
    }

    if (responseData.errors && typeof responseData.errors === 'object') {
      const firstField = Object.keys(responseData.errors)[0];
      if (firstField) {
        const fieldErrors = responseData.errors[firstField];
        if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
          return fieldErrors[0];
        }
        if (typeof fieldErrors === 'string') {
          return fieldErrors;
        }
      }
    }
  }

  const status = error.response?.status;
  switch (status) {
    case 400:
      return 'Nieprawidłowe dane';
    case 401:
      return 'Wymagane zalogowanie';
    case 403:
      return 'Brak uprawnień';
    case 404:
      return 'Nie znaleziono';
    case 409:
      return 'Taki rekord już istnieje';
    case 422:
      return 'Błąd walidacji';
    case 500:
      return 'Błąd serwera';
    default:
      return fallbackMessage;
  }
}
