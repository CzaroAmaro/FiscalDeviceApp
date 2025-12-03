<template>
  <div class="pa-4 pa-md-6">
    <h1 class="text-h4 mb-6">Pulpit - Wykresy</h1>

    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="mt-4">Ładowanie danych...</p>
    </div>

    <div v-else-if="error" class="text-center">
      <p class="text-h6 text-error">{{ error }}</p>
    </div>

    <div v-else-if="chartData">
      <v-row>
        <!-- Wykres 1: Zgłoszenia wg statusu -->
        <v-col cols="12" md="6" lg="5">
          <v-card class="fill-height">
            <v-card-text class="chart-container">
              <Pie
                v-if="ticketsByStatus && ticketsByStatus.datasets[0].data.length > 0"
                :data="ticketsByStatus"
                :options="{...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: 'Zgłoszenia wg statusu'}}}"
              />
              <div v-else class="d-flex align-center justify-center fill-height">Brak danych do wyświetlenia</div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Wykres 2: Urządzenia wg statusu -->
        <v-col cols="12" md="6" lg="7">
          <v-card class="fill-height">
            <v-card-text class="chart-container">
              <Doughnut
                v-if="devicesByStatus && devicesByStatus.datasets[0].data.length > 0"
                :data="devicesByStatus"
                :options="{...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: 'Urządzenia wg statusu'}}}"
              />
              <div v-else class="d-flex align-center justify-center fill-height">Brak danych do wyświetlenia</div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Wykres 3: Zgłoszenia w czasie -->
        <v-col cols="12">
          <v-card>
            <v-card-text class="chart-container" style="height: 400px;">
              <Bar
                v-if="workloadOverTime && workloadOverTime.datasets[0].data.length > 0"
                :data="workloadOverTime"
                :options="barChartOptions"
              />
              <div v-else class="d-flex align-center justify-center fill-height">Brak danych do wyświetlenia</div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Sekcja 4: Wygasające certyfikaty -->
        <v-col cols="12">
          <v-card>
            <v-card-title>Certyfikaty wygasające w ciągu 90 dni</v-card-title>
            <v-card-text>
              <v-table v-if="expiringCerts.length > 0" density="compact">
                <thead>
                <tr>
                  <th class="text-left">Serwisant</th>
                  <th class="text-left">Producent</th>
                  <th class="text-left">Numer certyfikatu</th>
                  <th class="text-left">Data wygaśnięcia</th>
                </tr>
                </thead>
                <tbody>
                <tr v-for="(cert, i) in expiringCerts" :key="i">
                  <td>{{ cert.technician }}</td>
                  <td>{{ cert.manufacturer }}</td>
                  <td>{{ cert.certificate_number }}</td>
                  <td>{{ cert.expiry_date }}</td>
                </tr>
                </tbody>
              </v-table>
              <p v-else>Brak certyfikatów wygasających w najbliższym czasie.</p>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useChartsStore } from '@/stores/charts';
import { Bar, Pie, Doughnut } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Colors
} from 'chart.js';

// Rejestracja komponentów Chart.js - to zostaje tak samo
ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Colors
);

// --- Store ---
const chartsStore = useChartsStore();
const { loading, data: chartData, error } = storeToRefs(chartsStore);

// --- Chart Options ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      font: {
        size: 16,
      },
    },
  },
};

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: 'Miesięczne obciążenie pracą wg typu zlecenia (ostatnie 12 m-cy)',
      font: {
        size: 16,
      },
    },
    // Opcjonalnie: Tooltip, który pokazuje sumę dla całego słupka
    tooltip: {
      mode: 'index' as const, // Pokazuje tooltip dla całej kategorii (miesiąca)
      intersect: false,
    },
  },
  scales: {
    x: {
      stacked: true, // PRAWIDŁOWO: Słupki w tej samej kategorii (miesiąc) będą stackowane
    },
    y: {
      stacked: true, // PRAWIDŁOWO: Wartości z różnych datasetów będą dodawane do siebie
      beginAtZero: true,
      title: {
        display: true,
        text: 'Liczba zleceń'
      }
    },
  },
};

// --- Computed properties for each chart (teraz odwołują się do store'a) ---
const ticketsByStatus = computed(() => {
  if (!chartData.value?.tickets_by_status) return null;
  return {
    labels: chartData.value.tickets_by_status.labels,
    datasets: [{
      label: 'Zgłoszenia',
      data: chartData.value.tickets_by_status.data,
    }],
  };
});

const workloadOverTime = computed(() => {
  // Sprawdzamy, czy dane istnieją i czy jest co najmniej jeden dataset
  if (!chartData.value?.workload_over_time || chartData.value.workload_over_time.datasets.length === 0) {
    return null;
  }
  return chartData.value.workload_over_time;
});

const devicesByStatus = computed(() => {
  if (!chartData.value?.devices_by_status) return null;
  return {
    labels: chartData.value.devices_by_status.labels,
    datasets: [{
      label: 'Urządzenia',
      data: chartData.value.devices_by_status.data,
    }],
  };
});

const expiringCerts = computed(() => {
  return chartData.value?.expiring_certifications || [];
});

// --- Lifecycle ---
onMounted(() => {
  // Jedyne co robimy, to wywołujemy akcję ze store'a
  chartsStore.fetchChartData();
});
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}
</style>
