<!--
Inspired by this set of tab controls:
https://svelte.dev/repl/8e68120858e5322272dc9136c4bb79cc?version=3.5.1
-->
<script context="module">
  export const ROTATOR = {};
</script>

<script>
  import { setContext, onMount } from "svelte";
  import { writable } from "svelte/store";

  // How long to show each child RotatorPanel, in seconds.
  export let time = 30;

  const panels = [];
  let panelIndex = -1;

  const currentPanel = writable(null);

  // This increments each time all the panels have been cycled through.
  const loopIndex = writable(0);

  // Store the registerPanel function and other data for panels to be able to access.
  setContext(ROTATOR, {
    registerPanel: (panel) => {
      panels.push(panel);
    },

    currentPanel,
    loopIndex,
  });

  onMount(() => {
    console.log("Rotator panel count:", panels.length);
    nextPanel();

    const interval = setInterval(() => {
      nextPanel();
    }, time * 1000);

    return () => {
      clearInterval(interval);
    };
  });

  function nextPanel() {
    if (panels.length === 0) {
      return;
    }
    if (panelIndex === panels.length - 1) {
      panelIndex = 0;
      loopIndex.update((n) => n + 1);
    } else {
      panelIndex += 1;
    }
    let current = panels[panelIndex];
    currentPanel.set(current);
    console.log(
      "Rotator currentPanel:",
      current.name ? current.name : "(unnamed)",
      "panelIndex:",
      panelIndex
    );
  }
</script>

<div>
  <slot />
</div>
