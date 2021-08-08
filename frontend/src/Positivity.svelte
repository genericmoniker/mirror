<script>
  // TODO: How can I make this component agnostic to being in a rotator or not?
  import { getContext } from "svelte";
  import { ROTATOR } from "./Rotator.svelte";

  const { loopIndex } = getContext(ROTATOR);

  const texts = [
    "You look great today!",
    "Hello, awesome!",
    "You rock!",
    "Be believing. Be happy. Don't get discouraged. Things will work out.  -- GBH",
    "Cynics do not contribute, skeptics do not create, doubters do not achieve. -- GBH",
    "Life is like an old-time rail journey—delays, sidetracks, smoke, dust, cinders, and jolts, interspersed only occasionally by beautiful vistas and thrilling bursts of speed. The trick is to thank the Lord for letting you have the ride. -- JLJ",
    "In all of living have much of fun and laughter. Life is to be enjoyed, not just endured. -- GBH",
    "Did you ever realize that it does not take very much in the way of brainpower to make remarks that may wound another? Try the opposite of that. Try handing out compliments. -- GBH",
  ];

  $: text = texts[$loopIndex % texts.length];
</script>

<p class="large">{text}</p>

<style>
  p {
    text-align: center;
  }
</style>
