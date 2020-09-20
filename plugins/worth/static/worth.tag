<worth>
    <div>
        <canvas ref="chart"></canvas>
    </div>

    <style>
        canvas {
            width: 400px !important;
        }
    </style>

    <script>
        // Get an array of the day of the month for the given full dates.
        getDates(fullDates) {
            return fullDates.map(
                function(d) {
                    return luxon.DateTime.fromISO(d).day
                }
            )
        }

        // Get an array of n zeros.
        zerosArray(n) {
            return Array.apply(null, Array(n))
                .map(Number.prototype.valueOf, 0)
        }

        updateChart(data) {
            if (data.length == 0) {
                return;  // nothing to show
            }

            Chart.defaults.global.defaultFontFamily = "Roboto";
            Chart.defaults.global.defaultFontColor = "white";
            Chart.defaults.global.defaultFontSize = 30;

            var values = Object.values(data)
            console.log("worth values: " + values)
            var labels = this.getDates(Object.keys(data))
            console.log("worth labels: " + labels)
            var zeros = this.zerosArray(values.length)
            var ctx = this.refs.chart.getContext('2d')
            var chart = new Chart(ctx, {
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

        tick() {
            $.getJSON("/worth/", function(json) {
                this.updateChart(json.values)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(12, 'hours').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</worth>
