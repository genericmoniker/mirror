<worth>
    <div>
        <canvas ref="chart" height="100"></canvas>
    </div>

    <script>
        // Get an array of the day of the month for the last n days.
        lastDates(n) {
            var dates = [];
            for (var i=n-1; i >= 0; i--) {
                var date = moment().startOf("day").subtract(i, "days");
                dates.push(date.date());
            }
            console.log(dates);
            return dates;
        }

        // Get an array of n zeros.
        zerosArray(n) {
            return Array.apply(null, Array(n))
                .map(Number.prototype.valueOf, 0);
        }

        updateChart(data) {
            if (data.length == 0) {
                return;  // nothing to show
            }
            var ctx = this.refs.chart.getContext('2d');
            var points = data.length;
            var labels = this.lastDates(points);
            var zeros = this.zerosArray(points);
            var chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        {
                            fill: false,
                            borderColor: 'rgb(255, 255, 255)',
                            data: data,
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
                    tooltips: {enabled: false}
                }
            });            
        }

        tick() {
            $.getJSON("/worth", function(json) {
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