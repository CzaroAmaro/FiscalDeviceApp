<template>
  <v-sheet
    class="d-flex align-center px-4"
    color="grey-darken-4"
    height="64"
  >
    <v-avatar v-if="!mini" class="me-3" color="primary" size="40" tile>
      <span class="white--text text-h6">FL</span>
    </v-avatar>
    <div v-if="!mini" class="text-subtitle-1 font-weight-medium">
      <router-link to="/" class="text-white text-decoration-none">
        FiscalLink
      </router-link>
    </div>
    <v-spacer />
    <v-btn icon="mdi-menu" variant="text" @click="mini = !mini" />
  </v-sheet>
  <v-divider />
</template>

<script lang="ts" setup>
// v-model:mini przekazywany z MainMenu.vue
const mini = defineModel<boolean>('mini')
</script>
