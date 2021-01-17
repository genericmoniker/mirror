<script>
    import { subscribe } from "./Events.svelte"

    let connected = true;
    let error = '';

    subscribe('connectivity.refresh', (e) => {
        let data = JSON.parse(e.data);
        connected = data.connected;
    });
</script>

{#if !connected}
<div id="conn" class="small">
    <img src="/images/connectivity-network-error.svg" alt="{error}"/>
</div>
{/if}

<style>
    div {
        display: block;
        height: 75px;
        position: fixed;
        bottom: 0;
        right: 0;
        z-index: 999;
        padding-right: 20px;
    }

    img {
        height: 100%;
    }
</style>
