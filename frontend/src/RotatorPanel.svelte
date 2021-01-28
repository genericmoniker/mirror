<script>
  import { getContext } from "svelte";
  import { ROTATOR } from "./Rotator.svelte";

  // Name of this panel -- mostly for logging/debugging.
  export let name = "";

  const panel = { name: name };
  const { registerPanel, currentPanel } = getContext(ROTATOR);

  registerPanel(panel);
</script>

<!--
The tab control this is based on used an {#if} block to show/hide the slot
content, but that doesn't allow child components to initialize at app startup,
so using hidden instead.
-->
<div hidden={$currentPanel !== panel}><slot /></div>
