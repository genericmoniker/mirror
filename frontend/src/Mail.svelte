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
<div class="large">
<p>{#each item.body_lines as line} {line} <br/> {/each}</p>
</div>
<p style="vertical-align: middle; color: #e1e1e1">
    <Icon data={envelope} scale="1.5" />
    <span style="padding-left: 5px">{item.sender}</span>
</p>
{/if}
