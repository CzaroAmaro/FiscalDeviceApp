<template>
  <v-dialog v-model="isDialogOpen" max-width="700px">
    <v-card v-if="device">
      <v-card-title>
        <span class="text-h5">Podgląd urządzenia</span>
        <v-spacer />
        <DeviceStatusChip :status="device.status" />
      </v-card-title>

      <v-card-text>
        <v-list density="compact">
          <v-list-item title="Marka i model" :subtitle="`${device.brand.name} ${device.model_name}`" />
          <v-divider />
          <v-list-item title="Numer unikatowy" :subtitle="device.unique_number" />
          <v-divider />
          <v-list-item title="Numer seryjny" :subtitle="device.serial_number" />
          <v-divider />
          <v-list-item title="Właściciel" :subtitle="`${device.owner.name} (NIP: ${device.owner.nip})`" />
          <v-divider />
          <v-list-item title="Data sprzedaży" :subtitle="device.sale_date || 'Brak danych'" />
          <v-divider />
          <v-list-item title="Data ostatniego przeglądu" :subtitle="device.last_service_date || 'Brak danych'" />
          <v-divider />
          <v-list-item title="Data następnego przeglądu" :subtitle="device.next_service_date || 'Brak danych'" />
          <v-divider />
          <v-list-subheader>Informacje dodatkowe</v-list-subheader>
          <v-list-item v-if="device.operating_instructions" title="Sposób użytkowania">
            <p class="text-body-2 text-grey-darken-1">{{ device.operating_instructions }}</p>
          </v-list-item>
          <v-list-item v-if="device.remarks" title="Uwagi">
            <p class="text-body-2 text-grey-darken-1">{{ device.remarks }}</p>
          </v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="isDialogOpen = false">Zamknij</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { FiscalDevice } from '@/types';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';

const props = defineProps<{
  modelValue: boolean;
  device: (FiscalDevice & { next_service_date?: string | null }) | null; // Dodajemy opcjonalne pole
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
}>();

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});
</script>
