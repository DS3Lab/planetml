<template>
    <div>
        <div id="world_map_view" class="mapview"></div>
        <Vue3EasyDataTable v-if="is_loaded" :headers="headers" :items="items"
            alternating show-index class="resouce_table">
        </Vue3EasyDataTable>
    </div>
</template>

<script setup>
import { onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist/plotly'
import { get_site_status, get_status_history, domain_to_name } from '../services/api'
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
            let perf = res.data[i].stats.SiteStat.avail_tflops
            if (perf < min_perfs) {
                min_perfs = perf
            }
            if (perf > max_perfs) {
                max_perfs = perf
            }
        }
        res.data.map(function (item) {
            data.push({
                type: "scattermapbox",
                name: item.name,
                lon: [parseFloat(item.lon)],
                lat: [parseFloat(item.lat)],
                text: [
                    "<b>" + item.name + "</b><br>" + item.stats.SiteStat.avail_tflops + " Available TFlops<br>" + 
                    item.stats.SiteStat.total_gpus + " GPUs" + "<br>" + 
                    item.stats.SiteStat.avail_gpus + " Available GPUs" + "<br>"+
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
        res.data.map(function (item) {
            items.value.push({
                'name': domain_to_name(item.site_identifier),
                'total_tflops': item.total_tflops,
                'total_gpu': item.total_gpus,
                'avail_gpu': item.avail_gpus,
                'domain': item.site_identifier,
                'created_at': item.created_at,
            })
            is_loaded.value = true
        })
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