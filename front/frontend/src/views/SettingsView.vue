<template>
  <v-container fluid class="settings-container">
    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <div class="page-header mb-6">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="56" variant="tonal" class="mr-4">
              <v-icon size="28">mdi-cog</v-icon>
            </v-avatar>
            <div>
              <h1 class="text-h4 font-weight-bold mb-1">
                {{ t('settings.title') }}
              </h1>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ t('settings.subtitle') }}
              </p>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="loading-state">
          <v-card rounded="lg" class="pa-8 text-center">
            <v-progress-circular
              indeterminate
              color="primary"
              size="48"
              class="mb-4"
            />
            <p class="text-body-1 text-medium-emphasis mb-0">
              {{ t('common.loading') }}
            </p>
          </v-card>
        </div>

        <v-alert
          v-else-if="error"
          type="error"
          variant="tonal"
          rounded="lg"
          class="mb-6"
        >
          <template #prepend>
            <v-icon>mdi-alert-circle</v-icon>
          </template>
          <div class="d-flex align-center justify-space-between">
            <span>{{ error }}</span>
            <v-btn
              variant="text"
              size="small"
              @click="retryFetch"
            >
              {{ t('common.retry') }}
            </v-btn>
          </div>
        </v-alert>

        <div v-else class="settings-content">
          <v-row>
            <v-col cols="12" md="3" class="d-none d-md-block">
              <v-card rounded="lg" class="settings-nav sticky-nav">
                <v-list nav density="comfortable" class="pa-2">
                  <v-list-item
                    v-for="section in navigationSections"
                    :key="section.id"
                    :value="section.id"
                    :active="activeSection === section.id"
                    rounded="lg"
                    @click="scrollToSection(section.id)"
                  >
                    <template #prepend>
                      <v-avatar
                        :color="activeSection === section.id ? 'primary' : 'grey'"
                        size="32"
                        variant="tonal"
                      >
                        <v-icon size="16">{{ section.icon }}</v-icon>
                      </v-avatar>
                    </template>
                    <v-list-item-title class="text-body-2">
                      {{ section.title }}
                    </v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>

            <v-col cols="12" md="9">
              <section id="company" class="settings-section">
                <CompanySettingsCard
                  :company-data="companyData"
                  :is-admin="isAdmin"
                  :is-saving="isSavingCompany"
                  @save="saveCompanySettings"
                  @update:company-data="updateCompanyData"
                />
              </section>

              <section id="profile" class="settings-section">
                <EditProfileCard />
              </section>

              <section id="email" class="settings-section">
                <ChangeEmailCard />
              </section>
            </v-col>
          </v-row>
        </div>
      </v-col>
    </v-row>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="bottom right"
    >
      <div class="d-flex align-center">
        <v-icon class="mr-2">
          {{ snackbar.color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
        </v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import api from '@/api';
import { useAuthStore } from '@/stores/auth';
import {useCompanyStore} from '@/stores/company.ts'
import CompanySettingsCard from '@/components/settings/CompanySettingsCard.vue';
import EditProfileCard from '@/components/settings/EditProfileForm.vue';
import ChangeEmailCard from '@/components/settings/ChangeEmailForm.vue';

interface Company {
  id: string;
  name: string;
}

const { t } = useI18n();
const authStore = useAuthStore();

const isLoading = ref(true);
const isSavingCompany = ref(false);
const error = ref<string | null>(null);
const activeSection = ref('company');
const companyStore = useCompanyStore();

const companyData = reactive<Partial<Company>>({
  name: '',
});

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success' as 'success' | 'error',
});

const isAdmin = computed(() => authStore.isAdmin);

const navigationSections = computed(() => [
  { id: 'company', title: t('settings.nav.company'), icon: 'mdi-office-building' },
  { id: 'profile', title: t('settings.nav.profile'), icon: 'mdi-account' },
  { id: 'email', title: t('settings.nav.email'), icon: 'mdi-email' },
]);

function updateCompanyData(data: Partial<Company>) {
  Object.assign(companyData, data);
}

async function fetchCompanyData() {
  isLoading.value = true;
  error.value = null;

  try {
    const response = await api.get<Company>('/company/me/');
    Object.assign(companyData, response.data);
  } catch (err) {
    error.value = t('settings.errors.loadFailed');
    console.error(err);
  } finally {
    isLoading.value = false;
  }
}

async function retryFetch() {
  await fetchCompanyData();
}

async function saveCompanySettings(name: string) {
  if (!isAdmin.value) {
    showSnackbar(t('settings.errors.noPermission'), 'error');
    return;
  }

  if (!name.trim()) {
    showSnackbar(t('settings.errors.emptyName'), 'error');
    return;
  }

  isSavingCompany.value = true;
  try {
    await api.patch('/company/me/', { name });
    companyData.name = name;
    companyStore.setCompanyName(name);
    showSnackbar(t('settings.company.saveSuccess'), 'success');
  } catch (err) {
    showSnackbar(t('settings.errors.saveFailed'), 'error');
    console.error(err);
  } finally {
    isSavingCompany.value = false;
  }
}

function scrollToSection(sectionId: string) {
  activeSection.value = sectionId;
  const element = document.getElementById(sectionId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function showSnackbar(text: string, color: 'success' | 'error') {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
}

let observer: IntersectionObserver | null = null;

function setupIntersectionObserver() {
  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          activeSection.value = entry.target.id;
        }
      });
    },
    { threshold: 0.3 }
  );

  navigationSections.value.forEach((section) => {
    const element = document.getElementById(section.id);
    if (element) {
      observer?.observe(element);
    }
  });
}

onMounted(async () => {
  await fetchCompanyData();
  setupIntersectionObserver();
});

onUnmounted(() => {
  observer?.disconnect();
});
</script>

<style scoped>
.settings-container {
  min-height: 100vh;
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.page-header {
  padding: 24px 0;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 48px 0;
}

.settings-content {
  padding-bottom: 48px;
}

.settings-nav {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
}

.sticky-nav {
  position: sticky;
  top: 80px;
}

.settings-section {
  margin-bottom: 24px;
  scroll-margin-top: 80px;
}

.settings-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  transition: all 0.3s ease;
}

.settings-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.2);
}

.card-header {
  padding: 20px 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.04) 0%,
    rgba(var(--v-theme-primary), 0.01) 100%
  );
}

@media (max-width: 960px) {
  .page-header {
    padding: 16px 0;
  }

  .settings-section {
    margin-bottom: 16px;
  }
}
</style>
