<script>
  import { subscribe } from "./Events.svelte";
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { faShoePrints } from "@fortawesome/free-solid-svg-icons";
  import { faCheckCircle } from "@fortawesome/free-solid-svg-icons";

  export let width;
  let height = 11;

  let canvas;
  let stepsStr = "0";
  let percent = 0;

  subscribe("activity.refresh", (e) => {
    let data = JSON.parse(e.data);
    let steps = data.steps;
    stepsStr = steps.toLocaleString();
    let stepsGoal = data.stepsGoal;
    percent = steps / stepsGoal;
    let barWidth = Math.min(1, percent) * width;
    drawProgressBar(barWidth);
  });

  function drawProgressBar(barWidth) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawLine(ctx, canvas.width, 1);
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
    drawProgressBar(0);
  });
</script>

<div id="component">
  <div id="text" style="width: {width}px">
    <Icon id="steps-icon" data={faShoePrints} scale="2" />
    &nbsp;
    {stepsStr}
    {#if percent >= 1}
      &nbsp;
      <span id="goal-icon"
        ><Icon id="goal-icon" data={faCheckCircle} scale="1.6" /></span
      >
    {/if}
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
  #goal-icon {
    opacity: 1;
    animation: fade 8s ease-in-out infinite;
  }
  @keyframes fade {
    0%,
    100% {
      opacity: 0;
    }
    50% {
      opacity: 1;
    }
  }
</style>
