<!-- Common functions for calendar components. -->
<script context="module">
  import { DateTime } from "luxon";

  export function updateData(items) {
    console.log("Calendar item count: " + items.length);
    let dataItems = [];
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
    return dataItems;
  }

  export function updateDisplay(dataItems) {
    let displayItems = [];
    for (let i = 0; i < dataItems.length; i++) {
      let item = dataItems[i];

      // Skip items in the past.
      if (item.start < DateTime.local()) {
        continue;
      }

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
    return displayItems;
  }
</script>
