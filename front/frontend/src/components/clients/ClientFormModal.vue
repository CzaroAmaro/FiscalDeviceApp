<template>
  <v-dialog :model-value="modelValue" @update:model-value="closeDialog" max-width="700px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="formData.name" :label="t('clients.forms.nameLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.nip" :label="t('clients.forms.nipLabel')" :rules="[rules.required, rules.nip]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.phone_number" :label="t('clients.forms.phoneLabel')" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formData.email" :label="t('clients.forms.emailLabel')" :rules="[rules.email]" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formData.address" :label="t('clients.forms.addressLabel')" />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">{{ t('common.cancel') }}</v-btn>
        <v-btn color="primary" @click="submitForm" :loading="isLoading">{{ t('common.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useClientsStore } from '@/stores/clients'
import type { Client } from '@/types'
import type { VForm } from 'vuetify/components'

const { t } = useI18n();

const props = defineProps<{ modelValue: boolean, editingClient: Client | null }>();
const emit = defineEmits(['update:modelValue', 'save-success']);

const clientsStore = useClientsStore();
const form = ref<VForm | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const initialFormData = { name: '', address: '', nip: '', phone_number: '', email: '' };
const formData = reactive({ ...initialFormData });

const isEditing = computed(() => !!props.editingClient);
const formTitle = computed(() => isEditing.value ? t('clients.forms.editTitle') : t('clients.forms.addTitle'));

watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.editingClient) {
    Object.assign(formData, props.editingClient);
  } else if (isOpen) {
    Object.assign(formData, initialFormData);
  }
});

const rules = computed(() => ({
  required: (v: string) => !!v || t('validation.required'),
  nip: (v: string) => /^\d{10}$/.test(v) || t('validation.nip'),
  email: (v: string) => !v || /.+@.+\..+/.test(v) || t('validation.email'),
}));

const closeDialog = () => emit('update:modelValue', false);

async function submitForm() {
  const { valid } = await form.value!.validate();
  if (!valid) return;

  isLoading.value = true;
  error.value = null;
  try {
    if (isEditing.value) {
      await clientsStore.updateClient(props.editingClient!.id, formData);
      emit('save-success', t('clients.forms.editSuccess'));
    } else {
      await clientsStore.addClient(formData);
      emit('save-success', t('clients.forms.addSuccess'));
    }
    closeDialog();
  } catch (err: any) {
    error.value = err.response?.data?.detail || t('common.serverError');
  } finally {
    isLoading.value = false;
  }
}
</script>
