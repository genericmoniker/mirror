<script>
    import { DateTime } from "luxon";
    import { onMount } from 'svelte';

    let now = DateTime.local();
    $: time = now.toLocaleString(DateTime.TIME_SIMPLE);
    $: date = now.toLocaleString(DateTime.DATE_HUGE);

    onMount(() => {
        const interval = setInterval(() => {
            now = DateTime.local();
        }, 1000);

        return () => {
            clearInterval(interval);
        };
    });
</script>

<div>
    <span class="large">{time}</span><br>
    <span>{date}</span>
</div>
