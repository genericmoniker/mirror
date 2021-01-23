<script>
    import { subscribe } from "./Events.svelte";
    import Icon from 'svelte-awesome';
    import { faEnvelope } from '@fortawesome/free-regular-svg-icons';

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
<div style="display:flex; align-items:center; color: #e1e1e1">
    <Icon data={faEnvelope} scale="1.7" />
    <span style="padding-left: 10px">{item.sender}</span>
</div>
{/if}
