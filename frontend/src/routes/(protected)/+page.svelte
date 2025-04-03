<script lang="ts">
	import type { PageData } from './$types';
	import Typewriter from '$lib/components/Typewriter.svelte';
	import type { AuthData } from '$lib/server/server.types';
	import { getContext } from 'svelte';
	import { getToasterState } from '$lib/components/toasts/toaster-state.svelte';
	import ActionCard from '$lib/components/ActionCard.svelte';
	import { goto } from '$app/navigation';

	let { data }: { data: PageData } = $props();

	const { user } = getContext<AuthData>('auth');

	const typed = [
		'Welcome to the range monitor, ' + user.username,
		'Big brother is always watching'
	];

	const notifications = getToasterState();

	notifications.create('Notice', 'Welcome to the range monitor ' + user.username, {
		preset: 'success'
	});
</script>

<Typewriter messages={typed} delay={2500} />




<style>
</style>
