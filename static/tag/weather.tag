<weather>
    <div class="large">
        <i class="large {icon}"></i>
        <span>{temp}</span>°
    </div>
    <div>
        <span>{summary}</span>
    </div>
    <table class="small"> <!-- 5 columns wide -->
        <tr>
            <td colspan="5">Feels like {feels}°</td>
        </tr>
        <tr>
            <td colspan="5">
                <i class="wi wi-strong-wind"></i>
                {wind} <sup class="tiny">mph</sup>
            </td>
        </tr>

        <tr>
            <td colspan="5">
                <i class="wi wi-sunrise"></i> {sunrise}
            </td>
        </tr>
        <tr>
            <td colspan="5">
                <i class="wi wi-sunset"></i> {sunset}
            </td>
        </tr>

        <tr><td colspan="4">&nbsp;</td></tr>

        <tr each={daily}>
            <td>{date}</td>
            <td><i class={icon}></i></td>
            <td>↑ <b>{max}</b></td>
            <td>↓ {min}</td>
            <td><i class='wi wi-umbrella'></i> {rain}<sup class='tiny'>%</sup></td>
        </tr>
    </table>

    <div class="small">
        <div id="weather_alert_title">{alert}</div>
        <!--div class="marquee">{alert_desc}</div-->
    </div>

    <style>
        #weather_alert_title {
            margin-top: 30px;
            font-weight: bold;
        }
        /*

        The marquee doesn't work too well... Choppy animation on the Pi,
        doesn't scroll the whole message, and seems to cause some update
        problem when there is a transition to having a weather alert and not
        having a weather alert.

        .marquee {
            margin: 0 auto;
            overflow: hidden;
            white-space: nowrap;
            box-sizing: border-box;
            animation: marquee 50s linear infinite;
        }

        @keyframes marquee {
            0%   { text-indent: 27.5em }
            100% { text-indent: -105em }
        }
        */
    </style>

    <script>
        iconClass(icon) {
            return 'wi wi-forecast-io-' + icon
        }

        updateCurrentConditions(data) {
            this.update({
                icon: this.iconClass(data.icon),
                temp: Math.round(data.temperature),
                summary: data.summary,
                feels: Math.round(data.apparentTemperature),
                wind: Math.round(data.windSpeed)
            })
        }

        updateForecast(data) {
            var today = data.data[0]
            var sunrise = moment.unix(today.sunriseTime).local()
            var sunset = moment.unix(today.sunsetTime).local()
            var limit = Math.min(5, data.data.length)
            var daily = []
            for (var i = 0; i < limit; i++) {
                var day = data.data[i]
                var date = moment.unix(day.time).local()
                daily.push({
                    date: date.format("ddd"),
                    icon: this.iconClass(day.icon),
                    max: Math.round(day.temperatureMax),
                    min: Math.round(day.temperatureMin),
                    rain: Math.round(day.precipProbability * 100)
                })
            }
            if (daily.length > 0) {
                daily[0].date = 'Today'
            }

            this.update({
                sunrise: sunrise.format("h:mm a"),
                sunset: sunset.format("h:mm a"),
                daily: daily
            })
        }

        updateAlert(data) {
            var alert = ''
            var desc = ''
            if (typeof data != 'undefined' && data.length > 0) {
                alert = data[0].title
                desc = data[0].description
            }
            this.update({
                alert: alert,
                alert_desc: desc
            })
        }

        tick() {
            $.getJSON("/weather", function(json) {
                this.updateCurrentConditions(json.currently)
                this.updateForecast(json.daily)
                this.updateAlert(json.alerts)
            }.bind(this))
        }

        var timer = setInterval(this.tick, moment.duration(5, 'minutes').asMilliseconds())

        this.on('mount', function() {
            this.tick()
        })

        this.on('unmount', function() {
            clearInterval(timer)
        })
    </script>
</weather>
