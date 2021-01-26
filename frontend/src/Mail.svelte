<script>
    import Icon from "svelte-awesome";
    import { faEnvelope } from "@fortawesome/free-regular-svg-icons";

    export let item;
</script>

{#if item}
    <div class="large">
        <p>
            {#each item.body_lines as line} {line} <br /> {/each}
        </p>
    </div>
    <div style="display:flex; align-items:center; color: #e1e1e1">
        <Icon data={faEnvelope} scale="1.7" />
        <span style="padding-left: 10px">{item.sender}</span>
    </div>
{/if}
