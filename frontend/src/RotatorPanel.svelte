<script>
  import { getContext, tick } from "svelte";
  import { ROTATOR } from "./Rotator.svelte";

  // Name of this panel -- mostly for logging/debugging.
  export let name = "";

  const panel = { name: name };
  const { registerPanel, currentPanel } = getContext(ROTATOR);

  let visible = false;

  $: {
    // Always set visible to false to allow fade-in even if the
    // current panel doesn't change.
    visible = false;
    if ($currentPanel === panel) {
      setTimeout(() => {
        visible = true;
      }, 2000);
    }
  }

  registerPanel(panel);
</script>

<!--
The tab control this is based on used an {#if} block to show/hide the slot
content, but that doesn't allow child components to initialize at app startup,
since they don't exist until added to the DOM.
-->
<div class:active={visible} class:inactive={!visible}>
  <slot />
</div>

<style>
  .active {
    transition: opacity 2s ease;
    opacity: 1;
    height: auto;
  }

  /* TODO: fade-out not working... why? */
  .inactive {
    transition: opacity 2s ease;
    opacity: 0;
    height: 0;
    overflow: hidden;
  }
</style>
