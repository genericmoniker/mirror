<script>
  import { getContext } from "svelte";
  import { ROTATOR } from "./Rotator.svelte";

  // Name of this panel -- mostly for logging/debugging.
  export let name = "";

  const panel = { name: name };
  const { registerPanel, currentPanel } = getContext(ROTATOR);

  $: visible = $currentPanel === panel;

  registerPanel(panel);
</script>

<!--
The tab control this is based on used an {#if} block to show/hide the slot
content, but that doesn't allow child components to initialize at app startup,
since they don't exist until added to the DOM.
-->
<div class:fade={!visible}>
  <slot />
</div>

<style>
  div {
    transition: 0.5s ease all;
  }

  .fade {
    opacity: 0;
  }
</style>
