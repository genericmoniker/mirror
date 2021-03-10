<script>
  import { subscribe } from "./Events.svelte";
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { faShoePrints } from "@fortawesome/free-solid-svg-icons";

  export let width;
  let height = 11;

  let canvas;
  let stepsStr = "0";

  subscribe("activity.refresh", (e) => {
    let data = JSON.parse(e.data);
    let steps = data.steps;
    stepsStr = steps.toLocaleString();
    let stepsGoal = data.stepsGoal;
    let percent = steps / stepsGoal;
    let barWidth = Math.min(1, percent) * width;
    drawBar(barWidth);
  });

  function drawCenterLine() {
    const ctx = canvas.getContext("2d");
    drawLine(ctx, canvas.width, 1);
  }

  function drawBar(barWidth) {
    const ctx = canvas.getContext("2d");
    drawLine(ctx, barWidth, height);
  }

  function drawLine(ctx, width, height) {
    let y = canvas.height / 2;
    const pad = 6; // leave space for rounded caps beyond line width
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = height;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.moveTo(pad, y);
    ctx.lineTo(width - pad, y);
    ctx.stroke();
  }

  onMount(() => {
    drawCenterLine();
    drawBar(100);
  });
</script>

<div id="component">
  <div id="text" style="width: {width}px">
    <Icon id="icon" data={faShoePrints} scale="2" />
    &nbsp;
    {stepsStr}
  </div>
  <canvas bind:this={canvas} {width} {height} />
</div>

<style>
  #component {
    padding-left: 10px;
  }
  #text {
    text-align: center;
    vertical-align: middle;
  }
</style>
