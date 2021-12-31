<script>
  import { subscribe } from "./Events.svelte";

  let name = "";
  let artists = "";
  let is_playing = false;

  subscribe("now_playing.refresh", (e) => {
    let data = JSON.parse(e.data);
    name = data.name;
    artists = data.artists.join(", ");
    is_playing = data.is_playing;
  });
</script>

{#if name}
  <div id="component">
    <div id="text">
      {#if is_playing}
        <img src="/images/now-playing.gif" alt="playing" width="40px" />
      {:else}
        <img src="/images/pause.png" alt="paused" width="40px" />
      {/if}
      &nbsp;
      <span class="large">{name}</span><br />
      {artists}
    </div>
  </div>
{/if}

<style>
  #component {
    padding-left: 10px;
  }
  #text {
    vertical-align: middle;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
</style>
