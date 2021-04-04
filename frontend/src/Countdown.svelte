<script>
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";
  import { onMount } from "svelte";

  const ONE_MINUTE = 60000;

  let dataItems = [];
  let displayItems = [];
  let today = DateTime.local();

  subscribe("calendars.refresh_countdown", (e) => {
    let rawItems = JSON.parse(e.data).items;
    updateData(rawItems);
    updateDisplay();
  });

  onMount(() => {
    const interval = setInterval(() => {
      let now = DateTime.local();
      if (now.toISODate() !== today.toISODate()) {
        today = now;
        console.log("Countdown day changed to: " + today.toISODate());
        updateDisplay();
      }
    }, ONE_MINUTE);

    return () => {
      clearInterval(interval);
    };
  });

  function updateData(items) {
    console.log("Countdown item count: " + items.length);
    dataItems = [];
    for (let i = 0; i < items.length; i++) {
      let item = items[i];
      let start = DateTime.fromISO(
        "dateTime" in item.start ? item.start.dateTime : item.start.date
      );
      dataItems.push({
        summary: item.summary,
        start: start,
      });
    }
  }

  function updateDisplay() {
    displayItems = [];
    for (let i = 0; i < dataItems.length; i++) {
      let item = dataItems[i];

      // toRelative will be something like "in 6 months".
      let fromNow = item.start.toRelative();

      // If fromNow doesn't include days, add them parenthetically.
      let fromNowDays = "";
      if (fromNow.indexOf("days") === -1) {
        fromNowDays =
          "(" +
          item.start.toRelative({ unit: "days" }).replace("in ", "") +
          ")";
      }

      // If fromNow is in the hours, just say "tomorrow".
      if (fromNow.indexOf("hour") != -1) {
        fromNow = "tomorrow";
      }

      displayItems.push({
        fromNow: fromNow,
        fromNowDays: fromNowDays,
        summary: item.summary,
      });
    }
  }
</script>

{#each displayItems as item}
  <div class="item">{item.summary} {item.fromNow} {item.fromNowDays}</div>
{/each}
