<script>
    import { subscribe } from "./Events.svelte";
    import { DateTime } from "luxon";

    let items = [];

    subscribe("calendar.refresh_coming_up", (e) => {
        items = [];
        let rawItems = JSON.parse(e.data).items;
        for (let i = 0; i < rawItems.length; i++) {
            let item = rawItems[i];
            let start = DateTime.fromISO(item.start.date);
            let fromNow = start.toRelative();
            if (fromNow.indexOf("hour") != -1) {
                fromNow = "tomorrow";
            }

            items.push({
                fromNow: fromNow,
                summary: item.summary,
            });
        }
    });
</script>

<style>
    .item {
        padding: 5px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        width: auto;
    }
</style>

<div class="small">
    {#each items as item}
        <div class="item">{item.summary} {item.fromNow}</div>
    {/each}
</div>
