<script>
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";
  import { onMount } from "svelte";

  let items = [];
  let now = DateTime.local();

  onMount(() => {
    const interval = setInterval(() => {
      now = DateTime.local();

      // Update items if any `current` value changed.
      var changed = false;
      var newItems = items.map((item) => {
        if ("startTime" in item) {
          var current = item.startTime <= now && item.endTime >= now;
          changed = changed || current !== item.current;
          return { ...item, current };
        }
        return item;
      });

      if (changed) {
        // Force update.
        items = [...newItems];
      }
    }, 1000);

    return () => {
      clearInterval(interval);
    };
  });

  subscribe("calendars.refresh_agenda", (e) => {
    items = [];
    let rawItems = JSON.parse(e.data).items;
    for (let i = 0; i < rawItems.length; i++) {
      let item = rawItems[i];
      if ("dateTime" in item.start) {
        var startTime = DateTime.fromISO(item.start.dateTime);
        var endTime = DateTime.fromISO(item.end.dateTime);
        var current = now >= startTime && now <= endTime;
        var start = startTime.toLocaleString(DateTime.TIME_SIMPLE);
        items.push({
          start: start,
          summary: item.summary,
          current: current,
          startTime: startTime,
          endTime: endTime,
        });
      } else {
        var start = "All Day - ";
        var current = false;
        items.push({
          start: start,
          summary: item.summary,
          current: current,
        });
      }
    }
  });
</script>

<table>
  {#if items.length === 0}<tr><td>No more jobs!</td></tr>{/if}
  {#each items as { start, summary, current }}
    <tr>
      <td>{start}</td>
      <td><span class:current>{summary}</span></td>
    </tr>
  {/each}
</table>

<style>
  table {
    width: auto;
    margin-right: 0px;
    margin-left: auto;
  }

  td {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 400px;
    text-align: left;
  }

  .current {
    font-weight: bold;
  }
</style>
