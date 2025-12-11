<!-- src/components/common/CountUp.vue -->
<template>
  <span>{{ formattedValue }}</span>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue';

interface Props {
  endVal: number;
  duration?: number;
  separator?: string;
}

const props = withDefaults(defineProps<Props>(), {
  duration: 1500,
  separator: ' ',
});

const currentValue = ref(0);

const formattedValue = computed(() => {
  return currentValue.value.toLocaleString('pl-PL');
});

const animate = (target: number) => {
  const start = currentValue.value;
  const startTime = performance.now();
  let animationFrame: number;

  const step = (currentTime: number) => {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / props.duration, 1);

    // Ease-out cubic
    const easeOut = 1 - Math.pow(1 - progress, 3);

    currentValue.value = Math.round(start + (target - start) * easeOut);

    if (progress < 1) {
      animationFrame = requestAnimationFrame(step);
    }
  };

  cancelAnimationFrame(animationFrame!);
  requestAnimationFrame(step);
};

watch(() => props.endVal, (newVal) => {
  animate(newVal);
});

onMounted(() => {
  animate(props.endVal);
});
</script>
