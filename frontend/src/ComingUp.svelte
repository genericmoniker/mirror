<script>
  import { updateData, updateDisplay } from "./Calendar.svelte";
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";
  import { onMount } from "svelte";

  const ONE_MINUTE = 60000;

  let dataItems = [];
  let displayItems = [];
  let today = DateTime.local();

  subscribe("calendars.refresh_coming_up", (e) => {
    let rawItems = JSON.parse(e.data).items;
    dataItems = updateData(rawItems);
    displayItems = updateDisplay(dataItems);
  });

  onMount(() => {
    const interval = setInterval(() => {
      let now = DateTime.local();
      if (now.toISODate() !== today.toISODate()) {
        today = now;
        console.log("Coming up day changed to: " + today.toISODate());
        displayItems = updateDisplay(dataItems);
      }
    }, ONE_MINUTE);

    return () => {
      clearInterval(interval);
    };
  });
</script>

{#each displayItems as item}
  <div class="item">{item.summary} {item.fromNow}</div>
{/each}

<style>
  .item {
    padding: 5px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    width: auto;
  }
</style>
