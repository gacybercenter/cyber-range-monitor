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

	const action = (href: string) => {
		return () => goto(href);
	};
</script>

<Typewriter messages={typed} delay={2500} />

<div class="row g-4">
	<ActionCard
		title="Guacamole"
		icon="fa-solid fa-clapperboard"
		imageSrc="/guacThumbnail.webp"
		action={action('/guacamole')}
		summary="Manage a view remote connections via the topology"
	>
		Visit
	</ActionCard>

	<ActionCard
		title="Openstack"
		icon="fa-solid fa-cloud-arrow-down"
		imageSrc="/openstack.webp"
		action={action('/openstack')}
		summary="placeholders placeholdersplaceholdersplaceholdersplaceholdersplaceholders"
	>
		Visit
	</ActionCard>
	<ActionCard
		title="Saltstack"
		icon="fa-solid fa-computer"
		imageSrc="/saltstack.webp"
		action={action('/saltstack')}
		summary="placeholdersplaceholdersplaceholdersplaceholdersplaceholdersplaceholders"
	>
		Visit
	</ActionCard>
</div>
