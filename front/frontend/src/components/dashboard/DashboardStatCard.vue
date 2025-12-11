<template>
  <v-card
    :class="['dashboard-stat-card', `dashboard-stat-card--${normalizedColor}`]"
    elevation="2"
    rounded="lg"
    :to="to"
    :ripple="!!to"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
  >
    <v-card-text class="card-content pa-5">
      <!-- Header z tytułem -->
      <div class="card-header">
        <p class="text-subtitle-1 text-medium-emphasis stat-label">
          {{ title }}
        </p>
      </div>

      <!-- Footer z wartością i ikoną -->
      <div class="card-footer">
        <div class="stat-value-wrapper">
          <!-- Loading state -->
          <template v-if="loading">
            <v-progress-circular
              indeterminate
              :color="normalizedColor"
              size="48"
            />
          </template>

          <!-- Value display -->
          <template v-else>
            <span class="text-h3 font-weight-bold stat-value" :class="`text-${normalizedColor}`">
              <CountUp
                v-if="typeof value === 'number'"
                :end-val="value"
                :duration="1500"
              />
              <template v-else>{{ value }}</template>
            </span>

            <v-chip
              v-if="trend !== undefined"
              :color="trend >= 0 ? 'success' : 'error'"
              size="small"
              class="ml-2"
              variant="tonal"
            >
              <v-icon size="14" start>
                {{ trend >= 0 ? 'mdi-trending-up' : 'mdi-trending-down' }}
              </v-icon>
              {{ Math.abs(trend) }}%
            </v-chip>
          </template>
        </div>

        <div
          :class="[
            'stat-icon-wrapper',
            `stat-icon-wrapper--${normalizedColor}`,
            { 'stat-icon-wrapper--hovered': isHovered }
          ]"
        >
          <v-icon :icon="icon" size="48" :color="normalizedColor" />
        </div>
      </div>

      <!-- Subtitle jeśli jest -->
      <p v-if="subtitle" class="text-caption text-medium-emphasis mt-2">
        {{ subtitle }}
      </p>

      <!-- Progress bar jeśli jest -->
      <v-progress-linear
        v-if="progress !== undefined"
        :model-value="progress"
        :color="normalizedColor"
        height="6"
        rounded
        class="mt-3"
      />
    </v-card-text>

    <!-- Action button jeśli jest -->
    <template v-if="actionText">
      <v-divider />
      <v-card-actions class="px-4 py-2">
        <v-btn
          :to="actionTo"
          variant="text"
          :color="normalizedColor"
          size="small"
          block
          class="text-none"
        >
          {{ actionText }}
          <v-icon end size="16">mdi-arrow-right</v-icon>
        </v-btn>
      </v-card-actions>
    </template>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import CountUp from '@/components/common/CountUp.vue';

interface Props {
  title: string;
  value: number | string;
  icon: string;
  color?: string;
  loading?: boolean;
  to?: RouteLocationRaw;
  subtitle?: string;
  trend?: number;
  progress?: number;
  actionText?: string;
  actionTo?: RouteLocationRaw;
}

const props = withDefaults(defineProps<Props>(), {
  color: 'primary',
  loading: false,
});

const isHovered = ref(false);

const colorMap: Record<string, string> = {
  primary: 'primary',
  secondary: 'secondary',
  success: 'success',
  warning: 'warning',
  error: 'error',
  info: 'info',
  red: 'error',
  teal: 'teal',
  green: 'success',
  orange: 'warning',
  blue: 'info',
};

const normalizedColor = computed(() => {
  return colorMap[props.color] || props.color;
});
</script>

<style scoped lang="scss">
.dashboard-stat-card {
  aspect-ratio: 1 / 1;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  overflow: hidden;
  position: relative;
  cursor: pointer;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
  }

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    transition: width 0.3s ease;
  }

  &--primary::before { background: rgb(var(--v-theme-primary)); }
  &--secondary::before { background: rgb(var(--v-theme-secondary)); }
  &--success::before { background: rgb(var(--v-theme-success)); }
  &--warning::before { background: rgb(var(--v-theme-warning)); }
  &--error::before { background: rgb(var(--v-theme-error)); }
  &--info::before { background: rgb(var(--v-theme-info)); }
  &--teal::before { background: #009688; }

  &:hover::before {
    width: 6px;
  }
}

.card-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.card-header {
  .stat-label {
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
  }
}

.card-footer {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-top: auto;
}

.stat-value-wrapper {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.stat-value {
  line-height: 1.2;
}

.stat-icon-wrapper {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  flex-shrink: 0;

  &--primary { background: rgba(var(--v-theme-primary), 0.1); }
  &--secondary { background: rgba(var(--v-theme-secondary), 0.1); }
  &--success { background: rgba(var(--v-theme-success), 0.1); }
  &--warning { background: rgba(var(--v-theme-warning), 0.1); }
  &--error { background: rgba(var(--v-theme-error), 0.1); }
  &--info { background: rgba(var(--v-theme-info), 0.1); }
  &--teal { background: rgba(0, 150, 136, 0.1); }

  &--hovered {
    transform: scale(1.1) rotate(5deg);

    &.stat-icon-wrapper--primary { background: rgba(var(--v-theme-primary), 0.2); }
    &.stat-icon-wrapper--secondary { background: rgba(var(--v-theme-secondary), 0.2); }
    &.stat-icon-wrapper--success { background: rgba(var(--v-theme-success), 0.2); }
    &.stat-icon-wrapper--warning { background: rgba(var(--v-theme-warning), 0.2); }
    &.stat-icon-wrapper--error { background: rgba(var(--v-theme-error), 0.2); }
    &.stat-icon-wrapper--info { background: rgba(var(--v-theme-info), 0.2); }
    &.stat-icon-wrapper--teal { background: rgba(0, 150, 136, 0.2); }
  }
}
</style>
