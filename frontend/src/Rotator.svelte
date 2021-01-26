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
    const currentPanel = writable(null);
    let index = -1;

    setContext(ROTATOR, {
        registerPanel: (panel) => {
            panels.push(panel);
        },

        currentPanel,
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
        index = index === panels.length - 1 ? 0 : index + 1;
        let current = panels[index];
        currentPanel.set(current);
        console.log(
            "Rotator currentPanel:",
            current.name ? current.name : "(unnamed)",
            "index:",
            index
        );
    }
</script>

<div>
    <slot />
</div>
