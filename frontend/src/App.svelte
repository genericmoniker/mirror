<script>
  import Activity from "./Activity.svelte";
  import Agenda from "./Agenda.svelte";
  import ComingUp from "./ComingUp.svelte";
  import Positivity from "./Positivity.svelte";
  import Connectivity from "./Connectivity.svelte";
  import Countdown from "./Countdown.svelte";
  import Clock from "./Clock.svelte";
  import Events from "./Events.svelte";
  import { subscribe } from "./Events.svelte";
  import LightTheWorld from "./LightTheWorld.svelte";
  import Mail from "./Mail.svelte";
  import Menu from "./Menu.svelte";
  import NowPlaying from "./NowPlaying.svelte";
  import Rotator from "./Rotator.svelte";
  import RotatorPanel from "./RotatorPanel.svelte";
  import Weather from "./Weather.svelte";
  import Word from "./Word.svelte";
  import Worth from "./Worth.svelte";

  let mailItems = [];

  subscribe("mail.refresh", (e) => {
    let data = JSON.parse(e.data);
    mailItems = data.items;
    console.log("Mail item count:", mailItems.length);
  });
</script>

<main>
  <section id="left">
    <Weather />
    <br />
    <Activity width="450" />
    <!-- FUTURE: Two up
    <table>
      <tr>
        <td><Activity width="225" /></td>
        <td><Activity width="225" /></td>
      </tr>
    </table>
     -->
    <br />
    <NowPlaying />
    <br />
    <Worth />
  </section>

  <section id="right">
    <Clock />
    <br />
    <Menu />
    <Agenda />
    <br />
    <ComingUp />
    <br />
    <Countdown />
  </section>

  <section id="bottom">
    <Rotator time="30">
      <!--
      <RotatorPanel name="light-the-world">
        <LightTheWorld />
      </RotatorPanel>
      -->
      <RotatorPanel name="word-ptbr">
        <Word event="word_ptbr.refresh" />
      </RotatorPanel>
      <RotatorPanel name="positivity">
        <Positivity />
      </RotatorPanel>
      {#each mailItems as item, i}
        <RotatorPanel name="mail {i}">
          <Mail {item} />
        </RotatorPanel>
      {/each}
    </Rotator>
  </section>

  <Connectivity />
  <Events />
</main>

<style>
  #left {
    float: left;
    width: 46%;
  }

  #right {
    float: right;
    width: 50%;
    text-align: right;
  }

  #bottom {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 35%;
  }
</style>
