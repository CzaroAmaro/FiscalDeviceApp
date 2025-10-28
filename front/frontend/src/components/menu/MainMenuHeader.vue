<template>
  <div>
    <v-list-item class="px-2" min-height="64" nav>
      <template #prepend>

        <v-btn
          v-if="rail"
          variant="text"
          icon="mdi-menu"
          @click.stop="$emit('update:rail', false)" />

        <v-avatar
          v-else
          class="mr-4"
          role="button"
          rounded="0"
          color="primary"
          @click="router.push('/')">
          <span class="text-h6">FL</span>
        </v-avatar>
      </template>

      <template #title>
        <v-list-item-title v-if="!rail" class="text-h6 font-weight-bold">
          FiscalLink
        </v-list-item-title>
      </template>

      <template #append>
        <v-btn
          v-if="!rail"
          variant="text"
          icon="mdi-menu"
          @click.stop="$emit('update:rail', true)"
        />
      </template>
    </v-list-item>
    <v-divider />
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

defineProps<{
  /**
   * Kontroluje, czy menu jest w trybie zwiniętym ('rail').
   * Odbierane z DefaultLayout przez v-model:rail.
   */
  rail: boolean;
}>();

defineEmits<{
  /**
   * Emituje zdarzenie, gdy stan 'rail' ma zostać zmieniony.
   */
  'update:rail': [value: boolean];
}>();

const router = useRouter();
</script>
