<template>
  <v-dialog v-model="isDialogOpen" max-width="500px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert
            v-if="form.state.error"
            type="error"
            density="compact"
            class="mb-4"
          >
            {{ form.state.error }}
          </v-alert>

          <v-text-field
            v-model="form.formData.name"
            :label="t('manufacturers.forms.nameLabel')"
            :rules="[rules.required]"
            autofocus
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" text @click="closeDialog">
          {{ t('common.cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          :loading="form.state.isSaving"
          @click="handleFormSubmit"
        >
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useForm } from '@/composables/useForm';
import type { Manufacturer } from '@/types';

type ManufacturerPayload = Pick<Manufacturer, 'name'>;

const props = defineProps<{
  modelValue: boolean;
  editingManufacturer: Manufacturer | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string, newManufacturer?: Manufacturer): void;
}>();

const { t } = useI18n();
const manufacturersStore = useManufacturersStore();
const { editingManufacturer } = toRefs(props);

const form = useForm<ManufacturerPayload, Manufacturer | null, Manufacturer>(
  { name: '' },
  editingManufacturer,
  (payload) => manufacturersStore.addManufacturer(payload),
  (id, payload) => manufacturersStore.updateManufacturer(id, payload)
);

const { formRef, isEditing } = form;

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const formTitle = computed(() =>
  isEditing.value
    ? t('manufacturers.forms.editTitle')
    : t('manufacturers.forms.addTitle')
);

const rules = computed(() => ({
  required: (v: string) => !!v || t('validation.required'),
}));

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  try {
    const savedItem = await form.submit();
    const message = isEditing.value
      ? t('manufacturers.forms.editSuccess')
      : t('manufacturers.forms.addSuccess');
    emit('save-success', message, isEditing.value ? undefined : savedItem);
    closeDialog();
  } catch (error) {
    console.error('Zapis producenta nie powiódł się:', error);
  }
}
</script>
