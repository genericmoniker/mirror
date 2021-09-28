<script>
  import { subscribe } from "./Events.svelte";

  export let event;

  let data = {};

  subscribe(event, (e) => {
    data = JSON.parse(e.data);
    console.log("Word data: ", data);
  });
</script>

<div class="center">
  <p><span class="huge divider">{data.word}</span></p>
  <p class="large">
    <span><i>{data.part_of_speech}</i></span> &#8226;
    <span>{data.translation}</span>
  </p>
  <p>{data.sentence}</p>
  <p>{data.sentence_translation}</p>
</div>

<style>
  .center {
    text-align: center;
  }

  .divider {
    border-bottom: 1px solid white;
  }
</style>
