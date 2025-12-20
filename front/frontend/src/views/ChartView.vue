<template>
  <div class="pa-4 pa-md-6">
    <h1 class="text-h4 mb-6">{{ t('charts.title') }}</h1>

    <div v-if="loading" class="text-center">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p class="mt-4">{{ t('common.loadingData') }}</p>
    </div>

    <div v-else-if="error" class="text-center">
      <p class="text-h6 text-error">{{ error }}</p>
    </div>

    <div v-else-if="chartData">
      <v-row>
        <v-col cols="12" md="6" lg="5">
          <v-card class="fill-height">
            <v-card-text class="chart-container">
              <Pie
                v-if="ticketsByStatus && ticketsByStatus.datasets[0].data.length > 0"
                :data="ticketsByStatus"
                :options="{...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: t('charts.ticketsByStatus.title')}}}"
              />
              <div v-else class="d-flex align-center justify-center fill-height">
                {{ t('charts.noData') }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6" lg="7">
          <v-card class="fill-height">
            <v-card-text class="chart-container">
              <Doughnut
                v-if="devicesByStatus && devicesByStatus.datasets[0].data.length > 0"
                :data="devicesByStatus"
                :options="{...chartOptions, plugins: {...chartOptions.plugins, title: {...chartOptions.plugins.title, text: t('charts.devicesByStatus.title')}}}"
              />
              <div v-else class="d-flex align-center justify-center fill-height">
                {{ t('charts.noData') }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12">
          <v-card>
            <v-card-text class="chart-container" style="height: 400px;">
              <Bar
                v-if="workloadOverTime && workloadOverTime.datasets[0].data.length > 0"
                :data="workloadOverTime"
                :options="barChartOptions"
              />
              <div v-else class="d-flex align-center justify-center fill-height">
                {{ t('charts.noData') }}
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12">
          <v-card>
            <v-card-title>{{ t('charts.expiringCertificates.title') }}</v-card-title>
            <v-card-text>
              <v-table v-if="expiringCerts.length > 0" density="compact">
                <thead>
                <tr>
                  <th class="text-left">{{ t('charts.expiringCertificates.headers.technician') }}</th>
                  <th class="text-left">{{ t('charts.expiringCertificates.headers.manufacturer') }}</th>
                  <th class="text-left">{{ t('charts.expiringCertificates.headers.certificateNumber') }}</th>
                  <th class="text-left">{{ t('charts.expiringCertificates.headers.expiryDate') }}</th>
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
              <p v-else>{{ t('charts.expiringCertificates.noCertificates') }}</p>
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
import { useI18n } from 'vue-i18n';
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

const { t } = useI18n();

const chartsStore = useChartsStore();
const { loading, data: chartData, error } = storeToRefs(chartsStore);

const chartOptions = computed(() => ({
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
}));

const barChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: true,
      text: t('charts.workloadOverTime.title'),
      font: {
        size: 16,
      },
    },
    tooltip: {
      mode: 'index' as const,
      intersect: false,
    },
  },
  scales: {
    x: {
      stacked: true,
    },
    y: {
      stacked: true,
      beginAtZero: true,
      title: {
        display: true,
        text: t('charts.workloadOverTime.yAxisLabel')
      }
    },
  },
}));

const ticketsByStatus = computed(() => {
  if (!chartData.value?.tickets_by_status) return null;
  return {
    labels: chartData.value.tickets_by_status.labels,
    datasets: [{
      label: t('charts.ticketsByStatus.datasetLabel'),
      data: chartData.value.tickets_by_status.data,
    }],
  };
});

const workloadOverTime = computed(() => {
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
      label: t('charts.devicesByStatus.datasetLabel'),
      data: chartData.value.devices_by_status.data,
    }],
  };
});

const expiringCerts = computed(() => {
  return chartData.value?.expiring_certifications || [];
});

onMounted(() => {
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
