<template>
  <v-card
    :loading="loading"
    class="stat-card"
    elevation="4"
    :to="to"
    link
  >
    <v-card-text class="d-flex flex-column justify-space-between fill-height">
      <div>
        <div class="text-subtitle-1 text-medium-emphasis">{{ title }}</div>
      </div>

      <div class="d-flex align-end justify-space-between mt-4">
        <div
          v-if="!loading"
          class="text-h3 font-weight-bold"
          :class="`text-${color}`"
        >
          {{ value }}
        </div>
        <div v-else class="text-h3">
          <v-progress-circular indeterminate :color="color"></v-progress-circular>
        </div>
        <v-icon :icon="icon" :color="color" size="48"></v-icon>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router';

defineProps<{
  title: string;
  value: string | number;
  icon: string;
  color?: string;
  loading?: boolean;
  to?: RouteLocationRaw;
}>();
</script>

<style scoped>
.stat-card {
  aspect-ratio: 1 / 1;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}
</style>
