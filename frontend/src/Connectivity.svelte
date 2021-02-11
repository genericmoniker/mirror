<script>
  import { subscribe } from "./Events.svelte";

  let connected = true;
  let error = "";

  subscribe("connectivity.refresh", (e) => {
    let data = JSON.parse(e.data);
    connected = data.connected;
    error = data.error;
  });
</script>

{#if !connected}
  <div id="conn">
    <span id="error" class="small">{error}</span>
    <img src="/images/connectivity-network-error.svg" alt={error} />
  </div>
{/if}

<style>
  #conn {
    display: block;
    height: 70px;
    position: fixed;
    bottom: 0;
    right: 0;
    z-index: 999;
    padding-right: 20px;
    padding-bottom: 10px;
  }

  img {
    height: 100%;
  }
</style>
