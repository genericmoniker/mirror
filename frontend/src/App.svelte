<script>
	import Agenda from './Agenda.svelte'
	import ComingUp from './ComingUp.svelte'
	import Countdown from './Countdown.svelte'
	import Clock from './Clock.svelte'
	import Mail from './Mail.svelte'
	import Weather from './Weather.svelte'
	import Worth from './Worth.svelte'

	import Connectivity from './Connectivity.svelte';
	import Events from './Events.svelte';
</script>

<style>
#left {
    float: left;
    width: 48%;
}

#right {
    float: right;
    width: 48%;
    text-align: right;
}

#bottom {
    position: fixed;
    bottom: 0;
    width: 100%;
    height: 35%;
}
</style>

<main>
	<section id="left">
		<Weather />
		<br>
		<Worth />
	</section>

	<section id="right">
		<Clock />
		<br>
		<Agenda />
		<br>
		<ComingUp />
		<br>
		<Countdown />
	</section>

	<section id="bottom">
		<Mail />
	</section>

	<Connectivity />
	<Events />
</main>
