<script>
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";
  import { onMount } from "svelte";

  const ONE_MINUTE = 60000;

  let data = {};
  let lunchToday = "";
  let today = DateTime.local();

  subscribe("menu.refresh", (e) => {
    data = JSON.parse(e.data);
    console.log("Menu data: ", data);
    lunchToday = data[today.toISODate()];
  });

  onMount(() => {
    const interval = setInterval(() => {
      let now = DateTime.local();
      if (now.toISODate() !== today.toISODate()) {
        today = now;
        console.log("Menu day changed to: " + today.toISODate());
        lunchToday = data[today.toISODate()];
      }
    }, ONE_MINUTE);

    return () => {
      clearInterval(interval);
    };
  });
</script>

{#if lunchToday}
  <div class="item">School lunch: {lunchToday}</div>
  <br />
{/if}
