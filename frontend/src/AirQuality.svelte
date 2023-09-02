<script>
  import { subscribe } from "./Events.svelte";

  let aqi = 0;
  let category = "";

  subscribe("air_quality.refresh", (e) => {
    let data = JSON.parse(e.data);
    aqi = data.AQI;
    category = data.Category.Name;
  });
</script>

{#if aqi > 0}
  <div style="display:flex;align-items:center;">
    <img id="aqi" src="/images/air_quality.svg" alt="aqi" width="40px" />
    &nbsp;{category} ({aqi}&nbsp;<sup class="small">aqi</sup>)
  </div>
{/if}

<style>
  #aqi {
    filter: invert(100%);
  }
</style>
