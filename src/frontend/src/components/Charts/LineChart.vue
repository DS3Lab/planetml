<script setup>
import { ref, watch, computed, onMounted } from "vue";
import {
  Chart,
  LineElement,
  PointElement,
  LineController,
  TimeScale,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Title,
} from "chart.js";
import 'chartjs-adapter-date-fns';

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
});

const root = ref(null);

let chart;

Chart.register(
  TimeScale,
  LineElement,
  PointElement,
  LineController,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  Title,
);

onMounted(() => {
  chart = new Chart(root.value, {
    type: "line",
    data: props.data,
    options: {
      plugins: {
        legend: {
          display: true,
        },
        title: {
          display: true,
          text: props.title
        }
      },
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          display: true,
        },
        x: {
          display: true,
          type: "time",
          time: {
            unit: 'hour',
            displayFormats: {
              hour: 'MMM-dd ha'
            }

          }
        },
      },
    },
  });
});

const chartData = computed(() => props.data);

watch(chartData, (data) => {
  if (chart) {
    chart.data = data;
    chart.update();
  }
});
</script>

<template>
  <canvas ref="root" />
</template>
