import { onMounted,ref, watch } from 'vue';

export function useCountUp(endValue: () => number, duration = 1500) {
  const displayValue = ref(0);
  let animationFrame: number;

  const animate = (target: number) => {
    const start = displayValue.value;
    const startTime = performance.now();

    const step = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      const easeOut = 1 - Math.pow(1 - progress, 3);

      displayValue.value = Math.round(start + (target - start) * easeOut);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(step);
      }
    };

    cancelAnimationFrame(animationFrame);
    animationFrame = requestAnimationFrame(step);
  };

  watch(endValue, (newVal) => {
    animate(newVal);
  });

  onMounted(() => {
    animate(endValue());
  });

  return displayValue;
}
