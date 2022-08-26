<script setup>
import { ref, onMounted } from "vue";
import {
  mdiChartTimelineVariant,
  mdiChartPie,
} from "@mdi/js";
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
let site_color_mapping = ref({})
let t_tflops_chartData = ref(null)
let t_gpus_chartData = ref(null)
let a_tflops_chartData = ref(null)
let a_gpus_chartData = ref(null)

function generate_chartData() {
  let t_tflops_datasets = []
  let t_gpus_datasets = []
  let a_tflops_datasets = []
  let a_gpus_datasets = []

  let labels = items.value.map(item => item.created_at)
  // find the unique site_identifiers from item
  let comp_sites = items.value.reduce((sites, item) => {
    if (sites.indexOf(item.name) === -1) {
      sites.push(item.name)
    }
    return sites
  }, [])
  // for each site in sites
  comp_sites.forEach(site => {
    let site_items = items.value.filter(item => item.name === site)
    let t_tflops_data = site_items.map(item => ({ "x": item.created_at, "y": item.total_tflops }))
    let a_tflops_data = site_items.map(item => ({ "x": item.created_at, "y": item.avail_tflops }))
    let t_gpus_data = site_items.map(item => ({ "x": item.created_at, "y": item.total_gpu }))
    let a_gpus_data = site_items.map(item => ({ "x": item.created_at, "y": item.avail_gpu }))
    // I am sure I will re-write this at some point... but leave it for now
    t_tflops_datasets.push({
      label: site,
      data: t_tflops_data,
      backgroundColor: site_color_mapping.value[site],
      borderColor: site_color_mapping.value[site],
      borderWidth: 1,
      fill: false,
    })
    a_tflops_datasets.push({
      label: site,
      data: a_tflops_data,
      backgroundColor: site_color_mapping.value[site],
      borderColor: site_color_mapping.value[site],
      borderWidth: 1,
      fill: false,
    })
    t_gpus_datasets.push({
      label: site,
      data: t_gpus_data,
      backgroundColor: site_color_mapping.value[site],
      borderColor: site_color_mapping.value[site],
      borderWidth: 1,
      fill: false,
    })
    a_gpus_datasets.push({
      label: site,
      data: a_gpus_data,
      backgroundColor: site_color_mapping.value[site],
      borderColor: site_color_mapping.value[site],
      borderWidth: 1,
      fill: false,
    })
  })
  t_tflops_chartData.value = {
    labels: labels,
    datasets: t_tflops_datasets
  };
  t_gpus_chartData.value = {
    labels: labels,
    datasets: t_gpus_datasets
  };
  a_tflops_chartData.value = {
    labels: labels,
    datasets: a_tflops_datasets
  };
  a_gpus_chartData.value = {
    labels: labels,
    datasets: a_gpus_datasets
  };
}

function update_site_stats() {
  get_site_status().then(function (res) {
    let data = []
    total_tflops.value = 0
    avail_gpus.value = 0
    avail_tflops.value = 0
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
      site_color_mapping.value[item.name] = item.color
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
    items.value = []
    // sort the data by its value
    let sorted_data = res.data.sort(function(a,b){return new Date(a.created_at) - new Date(b.created_at)});

    sorted_data.map(function (item) {
      items.value.push({
        'name': domain_to_name(item.site_identifier),
        'total_tflops': item.total_tflops,
        'avail_tflops': item.avail_tflops,
        'total_gpu': item.total_gpus,
        'avail_gpu': item.avail_gpus,
        'domain': item.site_identifier,
        'created_at': item.created_at,
      })
      is_loaded.value = true
    })
    generate_chartData()
  }).catch(function (err) {
    console.error(err)
  })
}

onMounted(() => {
  update_site_stats()
  setInterval(update_site_stats, 10000)
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

    <SectionTitleLineWithButton :icon="mdiChartPie" title="TFlops Status">
    </SectionTitleLineWithButton>

    <div class="grid grid-cols-2 gap-1 lg:grid-cols-2 mb-6" v-if="is_loaded">
      <CardBox class="mb-6">
        <div v-if="t_tflops_chartData">
          <line-chart :data="t_tflops_chartData" :title="'Total TFlops'"
            class="h-96" />
        </div>
      </CardBox>
      <CardBox class="mb-6">
        <div v-if="a_tflops_chartData">
          <line-chart :data="a_tflops_chartData" :title="'Available TFlops'"
            class="h-96" />
        </div>
      </CardBox>
    </div>

    <SectionTitleLineWithButton :icon="mdiChartPie"
      title="# GPUs Resources Status">
    </SectionTitleLineWithButton>

    <div class="grid grid-cols-2 gap-1 lg:grid-cols-2 mb-6" v-if="is_loaded">
      <CardBox class="mb-6">
        <div v-if="t_gpus_chartData">
          <line-chart :data="t_gpus_chartData" :title="'Total GPUs'"
            class="h-96" />
        </div>
      </CardBox>
      <CardBox class="mb-6">
        <div v-if="a_gpus_chartData">
          <line-chart :data="a_gpus_chartData" :title="'Available GPUs'"
            class="h-96" />
        </div>
      </CardBox>
    </div>

    <SectionTitleLineWithButton :icon="mdiChartPie" title="Raw Records">
    </SectionTitleLineWithButton>
    <CardBox class="mb-6">
      <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items"
        alternating show-index class="resouce_table">
      </Vue3EasyDataTable>
    </CardBox>

  </SectionMain>
</template>
