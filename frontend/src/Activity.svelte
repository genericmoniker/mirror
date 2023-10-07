<script>
  import { subscribe } from "./Events.svelte";
  import { onMount } from "svelte";
  import Icon from "svelte-awesome";
  import { faShoePrints } from "@fortawesome/free-solid-svg-icons";
  import { faCheckCircle } from "@fortawesome/free-solid-svg-icons";

  export let width;
  export let person = null;
  let height = 150;

  let canvas;
  let stepsStr = "0";
  let percent = 0; // 0-1

  subscribe("activity.refresh", (e) => {
    let data = JSON.parse(e.data)[person];
    let steps = data.steps;
    stepsStr = steps.toLocaleString();
    let stepsGoal = data.stepsGoal;
    percent = steps / stepsGoal;
    drawProgress(percent);
  });

  function drawProgress(percent) {
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawProgressRing(ctx, percent);
  }

  function drawProgressRing(ctx, percent) {
    let thinLineWidth = 1;
    let thickLineWidth = 6;
    let x = width / 2;
    let y = height / 2;
    let radius = height / 2 - thickLineWidth / 2;
    let rotation = Math.PI / 2; // amount to subtract to start with 0 at north
    let startAngle = 0 - rotation;
    let endAngleCircle = 2 * Math.PI - rotation;
    let endAnglePercent = 2 * Math.PI * percent - rotation;
    // Thin, full circle:
    drawArc(ctx, x, y, radius, startAngle, endAngleCircle, thinLineWidth);
    // Thick, progress:
    drawArc(ctx, x, y, radius, startAngle, endAnglePercent, thickLineWidth);
  }

  function drawArc(ctx, x, y, radius, start, end, lineWidth) {
    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = lineWidth;
    ctx.lineCap = "round";
    ctx.beginPath();
    ctx.arc(x, y, radius, start, end);
    ctx.stroke();
  }

  onMount(() => {
    drawProgress(0);
  });
</script>

<div id="component" class:stacked={true}>
  <div class="text" style="width: {width}px; height: {height}px;">
    <br />
    <!-- Cheat vertical center! -->
    <Icon id="steps-icon" data={faShoePrints} scale="2" />
    <br />
    {stepsStr}
    {#if percent >= 1}
      <br />
      <span id="goal-icon"
        ><Icon id="goal-icon" data={faCheckCircle} scale="1.6" /></span
      >
    {/if}
  </div>
  <canvas bind:this={canvas} {width} {height} />
  <div class="text" style="width: {width}px; height: {height}px;">
    {person}
  </div>
</div>

<style>
  #component {
    padding-left: 0px;
  }
  .text {
    text-align: center;
  }
  .stacked div {
    position: absolute;
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
      opacity: 0.5;
    }
  }
</style>
