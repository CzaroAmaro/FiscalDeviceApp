<template>
  <v-app>
    <RouterView v-if="isPublic" />
    <DefaultLayout v-else />
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const route = useRoute()

const isPublic = computed(() => route.meta.public === true)
</script>
