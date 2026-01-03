// src/utils/validationRules.ts

// Typy dla reguł walidacji Vuetify
type ValidationRule = (value: string) => boolean | string;

// Helper do tłumaczeń (przyjmuje funkcję t z i18n)
type TranslateFunction = (key: string, params?: Record<string, any>) => string;

export const createValidationRules = (t: TranslateFunction) => {
  return {

    required: (value: string): boolean | string => {
      return !!value?.trim() || t('validation.required');
    },


    username: {
      required: (value: string): boolean | string => {
        return !!value?.trim() || t('validation.username.required');
      },

      minLength: (value: string): boolean | string => {
        return !value || value.length >= 3 || t('validation.username.minLength', { min: 3 });
      },

      maxLength: (value: string): boolean | string => {
        return !value || value.length <= 30 || t('validation.username.maxLength', { max: 30 });
      },

      format: (value: string): boolean | string => {
        const pattern = /^[a-zA-Z0-9_-]+$/;
        return !value || pattern.test(value) || t('validation.username.format');
      },

      noStartWithNumber: (value: string): boolean | string => {
        return !value || !/^\d/.test(value) || t('validation.username.noStartWithNumber');
      },
    },


    email: {
      required: (value: string): boolean | string => {
        return !!value?.trim() || t('validation.email.required');
      },

      format: (value: string): boolean | string => {
        const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return !value || pattern.test(value) || t('validation.email.format');
      },

      maxLength: (value: string): boolean | string => {
        return !value || value.length <= 254 || t('validation.email.maxLength');
      },
    },


    password: {
      required: (value: string): boolean | string => {
        return !!value || t('validation.password.required');
      },

      minLength: (value: string): boolean | string => {
        return !value || value.length >= 8 || t('validation.password.minLength', { min: 8 });
      },

      maxLength: (value: string): boolean | string => {
        return !value || value.length <= 128 || t('validation.password.maxLength', { max: 128 });
      },

      hasUppercase: (value: string): boolean | string => {
        return !value || /[A-Z]/.test(value) || t('validation.password.hasUppercase');
      },

      hasLowercase: (value: string): boolean | string => {
        return !value || /[a-z]/.test(value) || t('validation.password.hasLowercase');
      },

      hasNumber: (value: string): boolean | string => {
        return !value || /\d/.test(value) || t('validation.password.hasNumber');
      },

      hasSpecialChar: (value: string): boolean | string => {
        return !value || /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~]/.test(value) || t('validation.password.hasSpecialChar');
      },

      noSpaces: (value: string): boolean | string => {
        return !value || !/\s/.test(value) || t('validation.password.noSpaces');
      },

      notCommon: (value: string): boolean | string => {
        const commonPasswords = [
          'password', 'password123', '123456789', 'qwerty123',
          'admin123', 'letmein', 'welcome', 'monkey123',
          'haslo123', 'zaq12wsx', 'qazwsx'
        ];
        const lowerValue = value?.toLowerCase() || '';
        return !commonPasswords.includes(lowerValue) || t('validation.password.notCommon');
      },
    },

    passwordConfirm: {
      required: (value: string): boolean | string => {
        return !!value || t('validation.passwordConfirm.required');
      },
      matches: (password: string) => (value: string): boolean | string => {
        return value === password || t('validation.passwordConfirm.matches');
      },
    },


    phone: {
      format: (value: string): boolean | string => {
        if (!value) return true; // Opcjonalne
        const pattern = /^(\+?[0-9]{1,4})?[-.\s]?(\(?\d{1,4}\)?)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$/;
        return pattern.test(value.replace(/\s/g, '')) || t('validation.phone.format');
      },
    },


    nip: {
      format: (value: string): boolean | string => {
        if (!value) return true;
        const cleaned = value.replace(/[-\s]/g, '');
        if (!/^\d{10}$/.test(cleaned)) {
          return t('validation.nip.format');
        }
        const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
        const sum = weights.reduce((acc, weight, index) => {
          return acc + weight * parseInt(cleaned[index], 10);
        }, 0);
        const checksum = sum % 11;
        return checksum === parseInt(cleaned[9], 10) || t('validation.nip.invalid');
      },
    },

    postalCode: {
      format: (value: string): boolean | string => {
        if (!value) return true;
        const pattern = /^\d{2}-\d{3}$/;
        return pattern.test(value) || t('validation.postalCode.format');
      },
    },
  };
};

export const combineRules = (...rules: ValidationRule[]): ValidationRule[] => {
  return rules;
};

export interface PasswordStrength {
  score: number; // 0-5
  label: string;
  color: string;
  percentage: number;
}

export const calculatePasswordStrength = (password: string, t: TranslateFunction): PasswordStrength => {
  if (!password) {
    return { score: 0, label: t('validation.password.strength.empty'), color: 'grey', percentage: 0 };
  }

  let score = 0;

  // Długość
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (password.length >= 16) score++;

  // Różnorodność znaków
  if (/[a-z]/.test(password)) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^a-zA-Z0-9]/.test(password)) score++;

  // Normalizacja do 0-5
  const normalizedScore = Math.min(5, Math.floor(score * 5 / 7));

  const strengthMap: Record<number, { label: string; color: string }> = {
    0: { label: t('validation.password.strength.veryWeak'), color: 'red-darken-2' },
    1: { label: t('validation.password.strength.weak'), color: 'red' },
    2: { label: t('validation.password.strength.fair'), color: 'orange' },
    3: { label: t('validation.password.strength.good'), color: 'yellow-darken-2' },
    4: { label: t('validation.password.strength.strong'), color: 'light-green' },
    5: { label: t('validation.password.strength.veryStrong'), color: 'green' },
  };

  return {
    score: normalizedScore,
    ...strengthMap[normalizedScore],
    percentage: (normalizedScore / 5) * 100,
  };
};
