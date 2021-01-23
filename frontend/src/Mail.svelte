<script>
    import { subscribe } from "./Events.svelte";
    import Icon from 'svelte-awesome';
    import { envelope } from 'svelte-awesome/icons';

    export let index = 0;
    let items = [];
    $: item = items.length ? items[index] : null;

    subscribe("mail.refresh", (e) => {
        let data = JSON.parse(e.data);
        items = data.items;
    });
</script>

{#if item}
<p>{#each item.body_lines as line} {line} <br/> {/each}</p>
<p class="small" style="vertical-align: middle; color: #e1e1e1">
    <Icon data={envelope} /> <span style="padding-left: 5px">{item.sender}</span>
</p>
{/if}
