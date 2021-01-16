<script>
    import { subscribe } from "./Events.svelte";
    import { DateTime } from "luxon";

    let items = [];

    subscribe("calendars.refresh_countdown", (e) => {
        items = [];
        let rawItems = JSON.parse(e.data).items;
        console.log("Countdown item count: " + rawItems.length);
        for (let i = 0; i < rawItems.length; i++) {
            let item = rawItems[i];
            let start = DateTime.fromISO(
                "dateTime" in item.start ? item.start.dateTime : item.start.date
            );

            // toRelative will be something like "in 6 months".
            let fromNow = start.toRelative();

            // If fromNow doesn't include days, add them parenthetically.
            let fromNowDays = "";
            if (fromNow.indexOf("days") === -1) {
                fromNowDays =
                    "(" +
                    start.toRelative({ unit: "days" }).replace("in ", "") +
                    ")";
            }

            // If fromNow is in the hours, just say "tomorrow".
            if (fromNow.indexOf("hour") != -1) {
                fromNow = "tomorrow";
            }

            items.push({
                fromNow: fromNow,
                fromNowDays: fromNowDays,
                summary: item.summary,
            });
        }
    });
</script>

<div class="small">
    {#each items as item}
        <div class="item">{item.summary} {item.fromNow} {item.fromNowDays}</div>
    {/each}
</div>
