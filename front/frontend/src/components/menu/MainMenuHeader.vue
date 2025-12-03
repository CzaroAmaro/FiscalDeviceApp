<template>
  <v-sheet
    class="d-flex align-center px-4"
    color="grey-darken-4"
    height="64"
  >
    <v-avatar v-if="!mini" class="me-3" size="40" tile>
      <img src="@/assets/only_logo.png" alt="Fiscal Service App Logo" class="auth-logo" />
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
const mini = defineModel<boolean>('mini')
</script>
<style scoped>
.auth-logo {
  max-height: 43px;
}
</style>
