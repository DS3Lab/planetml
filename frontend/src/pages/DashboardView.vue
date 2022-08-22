<script setup>
import { ref, onMounted } from "vue";
import {
  mdiChartTimelineVariant,
  mdiChartPie,
} from "@mdi/js";
import * as chartConfig from "@/components/Charts/chart.config.js";
import LineChart from "@/components/Charts/LineChart.vue";
import SectionMain from "@/components/SectionMain.vue";
import CardBoxWidget from "@/components/CardBoxWidget.vue";
import CardBox from "@/components/CardBox.vue";
import SectionTitleLineWithButton from "@/components/SectionTitleLineWithButton.vue";
import * as Plotly from 'plotly.js-dist/plotly'
import { get_site_status, get_status_history, domain_to_name } from '../services/api'
import Vue3EasyDataTable from 'vue3-easy-data-table'

let items = ref([])
let is_loaded = ref(false)
let total_tflops = ref(0)
let avail_gpus = ref(0)
let avail_tflops = ref(0)


const chartData = ref(null);
const fillChartData = () => {
  var days = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"];//x axes
  var litres = [150, 90, 95, 130, 85, 180, 85];//y axes
  chartData.value = {
    labels: days, //x-axes data 
    datasets: [{
      label: "Bar Chart",
      data: litres, //y-axes data 
    }]
  }
};

function update_site_stats() {
  total_tflops.value = 0
  avail_gpus.value = 0
  avail_tflops.value = 0
  get_site_status().then(function (res) {
    let data = []
    let min_perfs = 99999999
    let max_perfs = 0
    for (let i = 0; i < res.data.length; i++) {
      let perf = res.data[i].stats.SiteStat.avail_tflops
      if (perf < min_perfs) {
        min_perfs = perf
      }
      if (perf > max_perfs) {
        max_perfs = perf
      }
    }
    res.data.map(function (item) {
      total_tflops.value += item.stats.SiteStat.total_tflops
      avail_gpus.value += item.stats.SiteStat.avail_gpus
      avail_tflops.value += item.stats.SiteStat.avail_tflops
      data.push({
        type: "scattermapbox",
        name: item.name,
        lon: [parseFloat(item.lon)],
        lat: [parseFloat(item.lat)],
        text: [
          "<b>" + item.name + "</b><br>" + item.stats.SiteStat.avail_tflops + " Available TFlops<br>" +
          item.stats.SiteStat.total_gpus + " GPUs" + "<br>" +
          item.stats.SiteStat.avail_gpus + " Available GPUs" + "<br>" +
          item.stats.SiteStat.total_tflops + " Total TFlops"
        ],
        marker: {
          size: (item.stats.SiteStat.avail_tflops - min_perfs) / (max_perfs - min_perfs) * 15 + 10,
          color: item.color,
        }
      })
    })
    var layout = {
      dragmode: "zoom",
      mapbox: { style: "open-street-map", center: { lat: 45, lon: 0 }, zoom: 0.8 },
      margin: { r: 0, t: 0, b: 0, l: 0 }
    };
    Plotly.react('world_map_view', data, layout)
  }).catch(function (err) {
    console.error(err)
  })

  get_status_history().then(function (res) {
    let labels = []
    items.value = []
    let a_tflops = []
    let t_tflops = []

    res.data.map(function (item) {
      items.value.push({
        'name': domain_to_name(item.site_identifier),
        'total_tflops': item.total_tflops,
        'total_gpu': item.total_gpus,
        'avail_gpu': item.avail_gpus,
        'domain': item.site_identifier,
        'created_at': item.created_at,
      })
      labels.push(item.created_at)
      a_tflops.push(item.avail_tflops)
      t_tflops.push(item.total_tflops)
      is_loaded.value = true
    })
    let datasets = [{
      label: "Available TFlops",
      data: a_tflops, //y-axes data 
      backgroundColor: "rgba(54, 162, 235, 0.9)",
    }, {
      label: "Total TFlops",
      data: t_tflops, //y-axes data 
      backgroundColor: "rgba(255, 99, 132, 0.9)",
    }]
    chartData.value = {
      labels: labels, //x-axes data 
      datasets: datasets
    }
  }).catch(function (err) {
    console.error(err)
  })
}

onMounted(() => {
  update_site_stats()
  setInterval(update_site_stats, 10000)
  fillChartData();
})

const headers = [
  { text: "Name", value: "name" },
  { text: "Domain", value: "domain" },
  { text: "Total TFlops", value: "total_tflops", sortable: true },
  { text: "# GPU", value: "total_gpu", sortable: true },
  { text: "# Available GPU", value: "avail_gpu", sortable: true },
  { text: "Last Updated", value: "created_at", sortable: true },
];

</script>

<template>
  <SectionMain>
    <SectionTitleLineWithButton :icon="mdiChartTimelineVariant" title="Overview"
      main>
    </SectionTitleLineWithButton>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-3 mb-6" v-if="is_loaded">
      <CardBoxWidget color="text-emerald-500" :number="avail_tflops"
        suffix=" TFlops" label="Available TFlops" />
      <CardBoxWidget color="text-blue-500" :number="avail_gpus" prefix="# "
        label="Available GPUs" />
      <CardBoxWidget color="text-red-500" :number="total_tflops"
        suffix=" TFlops" label="Total TFlops" />
    </div>

    <SectionTitleLineWithButton :icon="mdiChartPie" title="Status Global View">
    </SectionTitleLineWithButton>

    <CardBox class="mb-6">
      <div id="world_map_view" class="mapview"></div>
    </CardBox>

    <CardBox class="mb-6">
      <div v-if="chartData">
        <line-chart :data="chartData" class="h-96" />
      </div>
    </CardBox>

    <CardBox class="mb-6">
      <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items"
        alternating show-index class="resouce_table">
      </Vue3EasyDataTable>
    </CardBox>


  </SectionMain>
</template>
