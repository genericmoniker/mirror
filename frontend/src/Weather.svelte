<script>
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";
  import AirQuality from "./AirQuality.svelte";

  let temp = "";
  let icon = "";
  let summary = "";
  let feels = "";
  let wind = "";
  let uvi = 0;
  let uviMax = 0;
  let sunrise = "";
  let sunset = "";
  let daily = [];
  let alerts = [];

  subscribe("weather.refresh", (e) => {
    let data = JSON.parse(e.data);

    temp = data.current.temp;
    icon = iconClass(data.current.weather[0].icon, data.current.weather[0].id);
    summary = data.current.weather[0].description;
    feels = data.current.feels_like;
    wind = data.current.wind_speed;
    uvi = data.current.uvi;
    uviMax = data.daily[0].uvi;
    sunrise = time(data.current.sunrise);
    sunset = time(data.current.sunset);
    daily = data.daily.slice(0, 5);
    alerts = "alerts" in data ? data.alerts : [];
  });

  function iconClass(icon, id) {
    // There are more icons for the weather "id", so we only
    // use the "icon" to figure out night or day.
    let time = ""; // Neutral in terms of night/day.
    let lastChar = icon.slice(-1);
    if (lastChar === "d") {
      time = "day-";
    } else if (lastChar === "n") {
      time = "night-";
    }
    return "wi wi-owm-" + time + id;
  }

  function time(dt) {
    return DateTime.fromSeconds(dt).toLocaleString(DateTime.TIME_SIMPLE);
  }

  function dayOfWeek(dt) {
    return DateTime.fromSeconds(dt).toFormat("ccc");
  }
</script>

<div class="huge">
  <i class="huge {icon}" /> <span>{Math.round(temp)}</span>°
</div>
<div><span id="summary" class="large">{summary}</span></div>
<br />

<table>
  <!-- Include these in the table for uniform horizontal spacing. -->
  <tr>
    <td colspan="5">Feels like {Math.round(feels)}°</td>
  </tr>
  <tr>
    <td colspan="5">
      <i class="wi wi-strong-wind" />
      {Math.round(wind)}
      <sup class="small">mph</sup>
    </td>
  </tr>
  <tr>
    <td colspan="5">
      <div style="display:flex;align-items:center;">
        <img
          id="uvi"
          src="/images/weather-glasses.svg"
          alt="uv index"
          width="40px"
        />
        &nbsp;{uvi.toFixed(1)}&nbsp; ↑ {uviMax.toFixed(1)}
      </div>
    </td>
  </tr>
  <tr>
    <td colspan="5">
      <AirQuality />
    </td>
  </tr>
  <tr>
    <td colspan="5"><i class="wi wi-sunrise" /> {sunrise}</td>
  </tr>
  <tr>
    <td colspan="5"><i class="wi wi-sunset" /> {sunset}</td>
  </tr>

  <tr><td colspan="5" /></tr>

  {#each daily as day, i}
    <tr>
      <td>{i === 0 ? "Today" : dayOfWeek(day.dt)}</td>
      <td><i class={iconClass("", day.weather[0].id)} /></td>
      <td>↑ <b>{Math.round(day.temp.max)}</b>°</td>
      <td>↓ {Math.round(day.temp.min)}°</td>
      <td>
        <i class="wi wi-umbrella" />
        {Math.round(day.pop * 100)}<sup class="small">%</sup>
      </td>
    </tr>
  {/each}
</table>

<div id="alerts">
  {#each alerts as alert}
    <div>{alert.event}</div>
  {/each}
</div>

<style>
  #summary {
    text-transform: capitalize;
  }

  #alerts {
    margin-top: 40px;
    font-weight: bold;
  }

  #uvi {
    filter: invert(100%);
  }

  td {
    padding-right: 20px;
  }
</style>
