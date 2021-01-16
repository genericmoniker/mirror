<script>
    import { subscribe } from "./Events.svelte";
    import { DateTime } from "luxon";

    let temp = '';
    let icon = '';
    let summary = '';
    let feels = '';
    let wind = '';
    let sunrise = '';
    let sunset = '';
    let daily = [];
    let alerts = [];

    subscribe("weather.refresh", (e) => {
        let data = JSON.parse(e.data);

        temp = data.current.temp;
        icon = iconClass(data.current.weather[0].icon, data.current.weather[0].id);
        summary = data.current.weather[0].description;
        feels = data.current.feels_like;
        wind = data.current.wind_speed;
        sunrise = time(data.current.sunrise);
        sunset = time(data.current.sunset);
        daily = data.daily.slice(0, 5);
        alerts = ('alerts' in data) ? data.alerts : [];
    });

    function iconClass(icon, id) {
        // There are more icons for the weather "id", so we only
        // use the "icon" to figure out night or day.
        let time = ''; // Neutral in terms of night/day.
        let lastChar = icon.slice(-1);
        if (lastChar === 'd') {
            time = 'day-';
        } else if (lastChar === 'n') {
            time = 'night-'
        }
        return 'wi wi-owm-' + time + id;
    }

    function time(dt) {
        return DateTime.fromSeconds(dt).toLocaleString(DateTime.TIME_SIMPLE);
    }

    function dayOfWeek(dt) {
        return DateTime.fromSeconds(dt).toFormat('ccc');
    }

</script>


<style>
    #summary {
        text-transform: capitalize;
    }

    #weather_alerts {
        margin-top: 30px;
        font-weight: bold;
    }
</style>

<div class="large"><i class="large {icon}" /> <span>{Math.round(temp)}</span>°</div>
<div><span id="summary">{summary}</span></div>
<table class="small">
    <!-- 5 columns wide -->
    <tr>
        <td colspan="5">Feels like {Math.round(feels)}°</td>
    </tr>
    <tr>
        <td colspan="5">
            <i class="wi wi-strong-wind" />
            {wind}
            <sup class="tiny">mph</sup>
        </td>
    </tr>

    <tr>
        <td colspan="5"><i class="wi wi-sunrise" /> {sunrise}</td>
    </tr>
    <tr>
        <td colspan="5"><i class="wi wi-sunset" /> {sunset}</td>
    </tr>

    <tr>
        <td colspan="4">&nbsp;</td>
    </tr>

    {#each daily as day, i}
    <tr>
        <td>{(i === 0) ? 'Today' : dayOfWeek(day.dt)}</td>
        <td><i class={iconClass('', day.weather[0].id)}></i></td>
        <td>↑ <b>{Math.round(day.temp.max)}</b></td>
        <td>↓ {Math.round(day.temp.min)}</td>
        <td><i class='wi wi-umbrella'></i> {day.pop * 100}<sup class='tiny'>%</sup></td>
    </tr>
    {/each}

    <div id="weather_alerts" class="small">
        {#each alerts as alert}
        <div>{alert.event}</div>
        {/each}
    </div>

</table>
