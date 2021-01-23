<script>
    import { subscribe } from "./Events.svelte";
    import { Chart } from "chart.js"
    import { DateTime } from "luxon";

    let canvas;

    subscribe("worth.refresh", (e) => {
        let data = JSON.parse(e.data);
        updateChart(data.values);
    });

    function getDates(fullDates) {
        return fullDates.map(
            function(d) {
                return DateTime.fromISO(d).day
            }
        )
    }

    // Get an array of n zeros.
    function zerosArray(n) {
        return Array.apply(null, Array(n))
            .map(Number.prototype.valueOf, 0)
    }

    function updateChart(data) {
        if (data.length == 0) {
            return;  // nothing to show
        }

        Chart.defaults.global.defaultFontFamily = "Roboto";
        Chart.defaults.global.defaultFontColor = "white";
        Chart.defaults.global.defaultFontSize = 30;

        const values = Object.values(data);
        console.log("worth values: " + values);
        const labels = getDates(Object.keys(data));
        console.log("worth labels: " + labels);
        const zeros = zerosArray(values.length);
        const ctx = canvas.getContext('2d');
        let chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        fill: false,
                        borderColor: 'rgb(255, 255, 255)',
                        data: values,
                    },
                    // This is just to draw the x-axis:
                    {
                        fill: false,
                        radius: 0,
                        borderColor: 'rgb(100, 100, 100)',
                        data: zeros,
                    }
                ]
            },
            options: {
                legend: {display: false},
                tooltips: {enabled: false},
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    yAxes: [{
                        ticks: {
                            fontColor: "white",
                        }
                    }],
                    xAxes: [{
                        ticks: {
                            fontColor: "white",
                        }
                    }]
                }
            }
        })
    }

</script>

<div>
    <canvas bind:this={canvas}></canvas>
</div>

<style>
    canvas {
        width: 475px !important;
    }
</style>
