<template>
  <v-sheet color="grey-darken-4" height="64" class="d-flex align-center px-2">
    <!-- Wersja rozwinięta -->
    <template v-if="!mini">
      <v-avatar class="mr-3" color="primary" rounded="0" role="button" @click="router.push('/')">
        <span class="text-h6">FL</span>
      </v-avatar>
      <v-list-item-title class="text-h6 font-weight-bold">
        FiscalLink
      </v-list-item-title>
      <v-spacer />
      <v-btn
        variant="text"
        icon="mdi-menu"
        aria-label="Zwiń menu"
        @click.stop="mini = true"
      />
    </template>

    <!-- Wersja zwinięta -->
    <template v-else>
      <v-btn
        class="mx-auto"
        variant="text"
        icon="mdi-menu"
        aria-label="Rozwiń menu"
        @click.stop="mini = false"
      />
    </template>
  </v-sheet>
  <v-divider />
</template>

<script lang="ts" setup>
import { useRouter } from 'vue-router';

// v-model:mini przekazywany z MainMenu.vue
const mini = defineModel<boolean>('mini');

const router = useRouter();
</script>
