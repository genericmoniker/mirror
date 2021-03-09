<script>
  import { subscribe } from "./Events.svelte";
  import Icon from "svelte-awesome";
  import { faShoePrints } from "@fortawesome/free-solid-svg-icons";

  export let width;

  let steps = 0;
  let barWidth;

  subscribe("activity.refresh", (e) => {
    let data = JSON.parse(e.data);
    steps = data.steps;
    let stepsGoal = data.stepsGoal;
    let percent = steps / stepsGoal;
    barWidth = Math.min(1, percent) * width;
  });
</script>

<div id="component">
  <div id="box" style="width: {width}px">
    <div id="bar" style="width: {barWidth}px">
      <div id="text" style="width: {width}px">
        <Icon id="icon" data={faShoePrints} scale="2" />
        {steps}
      </div>
    </div>
  </div>
</div>

<style>
  #component {
    padding-left: 10px;
  }

  #box {
    border: 1px solid white;
    border-radius: 5px;
  }

  #bar {
    background-color: rgb(231, 231, 231);
    border-radius: 2px;
  }

  #text {
    text-align: center;
    vertical-align: middle;
    mix-blend-mode: difference;
  }
</style>
