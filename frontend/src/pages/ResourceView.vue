<template>
    <div>
        <div id="tester" class="mapview"></div>
        <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items" alternating show-index class="resouce_table">
        </Vue3EasyDataTable>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist/plotly'
import { get_site_status } from '../services/api'
import { ref } from 'vue'
import Vue3EasyDataTable from 'vue3-easy-data-table'

let items = ref([])
let is_loaded = ref(false)

function update_site_stats() {
    get_site_status().then(function (res) {
        let data = []
        let min_perfs = 99999999
        let max_perfs = 0
        for (let i = 0; i < res.data.length; i++) {
            let perf = res.data[i].stats.SiteStat.total_perfs
            if (perf < min_perfs) {
                min_perfs = perf
            }
            if (perf > max_perfs) {
                max_perfs = perf
            }
        }
        items.value = []
        res.data.map(function (item) {
            items.value.push({
                'name': item.name,
                'perf': item.stats.SiteStat.total_perfs,
                'gpu': item.stats.SiteStat.num_gpu,
                'cpu': item.stats.SiteStat.num_cpu,
                'domain': item.identifier,
                'created_at': item.created_at,
            })
            data.push({
                type: "scattermapbox",
                name: item.name,
                lon: [parseFloat(item.lon)],
                lat: [parseFloat(item.lat)],
                text: ["<b>" + item.name + "</b><br>" + item.stats.SiteStat.total_perfs + " TFlops<br>" + item.stats.SiteStat.num_gpu + " GPUs" + "<br>" + item.stats.SiteStat.num_cpu + " CPUs"],
                marker: {
                    size: (item.stats.SiteStat.total_perfs - min_perfs) / (max_perfs - min_perfs) * 2 + 10,

                }
            })
        })
        is_loaded.value = true
        var layout = {
            dragmode: "zoom",
            mapbox: { style: "open-street-map", center: { lat: 45, lon: 0 }, zoom: 0.8 },
            margin: { r: 0, t: 0, b: 0, l: 0 }
        };
        Plotly.react('tester', data, layout)

        
    }).catch(function (err) {
        console.log(err)
    })
}

onMounted(() => {
    update_site_stats()
    setInterval(update_site_stats, 10000)
})

const headers = [
    { text: "Name", value: "name" },
    { text: "Domain", value: "domain" },
    { text: "Total Perfs", value: "perf", sortable: true },
    { text: "# GPU", value: "gpu", sortable: true },
    { text: "# CPU", value: "cpu", sortable: true },
    { text: "Last Updated", value: "created_at", sortable: true },
];


</script>

<style scoped>
.mapview {
    margin-left: auto;
    margin-right: auto;
    width: 80%;
    height: 100%;
}
.resouce_table {
    margin-top: 2.5rem;
}
</style>