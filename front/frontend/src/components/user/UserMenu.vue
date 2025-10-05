<template>
  <v-card min-width="250" elevation="2">
    <v-list density="compact">
      <!-- 1. Informacje o użytkowniku -->
      <v-list-item lines="two" class="px-4 pt-2 pb-3">
        <template v-slot:prepend>
          <v-avatar color="primary" icon="mdi-account-circle"></v-avatar>
        </template>
        <v-list-item-title class="font-weight-bold">
          <!-- W przyszłości nazwa użytkownika ze store'a -->
          Jan Kowalski
        </v-list-item-title>
        <v-list-item-subtitle>
          <!-- W przyszłości email użytkownika ze store'a -->
          jan.kowalski@example.com
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider></v-divider>

      <!-- 2. Panel z preferencjami -->
      <v-list-group value="Preferences">
        <template v-slot:activator="{ props }">
          <v-list-item
            v-bind="props"
            prepend-icon="mdi-cog-outline"
            title="Preferencje"
            @click.stop
          ></v-list-item>
        </template>

        <!-- Tu dodasz w przyszłości opcje -->
        <v-list-item
          prepend-icon="mdi-theme-light-dark"
          title="Zmień motyw"
          value="theme"
          disabled
        ></v-list-item>
        <v-list-item
          prepend-icon="mdi-bell-outline"
          title="Powiadomienia"
          value="notifications"
          disabled
        ></v-list-item>
      </v-list-group>

      <v-divider/>

      <!-- 3. Przycisk wylogowania -->
      <v-list-item
        prepend-icon="mdi-logout"
        title="Wyloguj"
        @click="onLogout"
        class="text-error"
      ></v-list-item>
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
// Definiujemy zdarzenie (event), które komponent może "wyemitować" do rodzica
const emit = defineEmits<{
  (e: 'logout'): void
}>()

const onLogout = () => {
  emit('logout')
}
</script>
