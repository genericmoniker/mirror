<script>
  // TODO: How can I make this component agnostic to being in a rotator or not?
  import { getContext } from "svelte";
  import { ROTATOR } from "./Rotator.svelte";

  const { loopIndex } = getContext(ROTATOR);

  const compliments = [
    "You look great today!",
    "Hello, awesome!",
    "I look so better with you standing there!",
    "You rock!",
  ];

  $: compliment = compliments[$loopIndex % compliments.length];
</script>

<p class="huge">{compliment}</p>

<style>
  p {
    text-align: center;
  }
</style>
