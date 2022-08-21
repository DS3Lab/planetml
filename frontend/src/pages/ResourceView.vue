<script setup>
import { onMounted } from 'vue';
import * as Plotly from 'plotly.js-dist/plotly'

onMounted(() => {
    var data = [
        {
            type: "scattermapbox",
            text: "123",
            lon: [0],
            lat: [48.4113],
            marker: { color: "fuchsia", size: 4 }
        }
    ];
    console.log(data)
    var layout = {
        dragmode: "zoom",
        mapbox: { style: "open-street-map", center: { lat: 0, lon: 48.4113 }, zoom: 0 },
        margin: { r: 0, t: 0, b: 0, l: 0 }
    };

    Plotly.newPlot("tester", data, layout);
})
</script>

<template>
    <div id="tester"></div>
</template>