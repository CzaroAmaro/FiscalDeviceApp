import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

import { calculatePasswordStrength, createValidationRules, type PasswordStrength } from '@/utils/validationRules';

export const useValidation = () => {
  const { t } = useI18n();
  const rules = createValidationRules(t);

  const getPasswordStrength = (password: string): PasswordStrength => {
    return calculatePasswordStrength(password, t);
  };

  return {
    rules,
    getPasswordStrength,
  };
};
