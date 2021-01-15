<script>
	import Clock from './Clock.svelte'
	import Agenda from './Agenda.svelte'
	import ComingUp from './ComingUp.svelte'
	import Countdown from './Countdown.svelte'
	import Weather from './Weather.svelte'

	import Connectivity from './Connectivity.svelte';
	import Events from './Events.svelte';
</script>

<main>
	<Clock />
	<Agenda />
	<ComingUp />
	<Countdown />
	<Weather />

	<Connectivity />
	<Events />
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>