<script setup>
import { onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist/plotly'
import { get_site_status } from '../services/api'

onMounted(() => {
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
        console.log(max_perfs)
        console.log(min_perfs)
        res.data.map(function (item) {
            console.log(res)
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
        console.log(data)
        var layout = {
            dragmode: "zoom",
            mapbox: { style: "open-street-map", center: { lat: 45, lon: 0 }, zoom: 0.8 },
            margin: { r: 0, t: 0, b: 0, l: 0 }
        };
        Plotly.newPlot("tester", data, layout);
    }).catch(function (err) {
        console.log(err)
    })
})
</script>

<template>
    <div id="tester" class="mapview"></div>
</template>

<style scoped>
.mapview {
    margin-left: auto;
    margin-right: auto;
    width: 80%;
    height: 100%;
}
</style>