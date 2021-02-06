<script>
  import { subscribe } from "./Events.svelte";
  import { DateTime } from "luxon";

  let items = [];

  subscribe("calendars.refresh_agenda", (e) => {
    items = [];
    let rawItems = JSON.parse(e.data).items;
    for (let i = 0; i < rawItems.length; i++) {
      let item = rawItems[i];
      if ("dateTime" in item.start) {
        var startTime = DateTime.fromISO(item.start.dateTime);
        var start = startTime.toLocaleString(DateTime.TIME_SIMPLE);
      } else {
        var start = "All Day - ";
      }
      items.push({
        start: start,
        summary: item.summary,
      });
    }
  });
</script>

<table>
  {#if items.length === 0}<tr><td>No more jobs!</td></tr>{/if}
  {#each items as item}
    <tr>
      <td>{item.start}</td>
      <td>{item.summary}</td>
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
</style>
