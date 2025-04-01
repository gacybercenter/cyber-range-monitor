<script lang="ts">
	import type { LayoutData } from './$types';
	import { getContext, onMount, setContext, type Snippet } from 'svelte';
	import { NavOption, Navbar, DropdownNav } from '$lib/components/navigation';
	import Header from '$lib/components/header/Header.svelte';
	import Notifications from '$lib/components/toasts/Notifications.svelte';
	import type { AuthData } from '$lib/server/server.types';
	import { setNotificationState } from '$lib/components/toasts/notification-state.svelte';

	setNotificationState();
	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	setContext<AuthData>('auth', {
		user: data.user,
		apiKey: data.apiKey
	});

	const auth = getContext<AuthData>('auth');

	let navOpen = $state(false);
</script>

<Header starCount={200} onclick={() => (navOpen = !navOpen)} user={auth.user} isOpen={navOpen} />

<Navbar active={navOpen}>
	<NavOption href="/" title="Home" icon="fa-solid fa-house" />
	<NavOption href="/users" title="users" icon="fa-regular fa-circle-user" />
	<NavOption href="/datasources" title="datasources" icon="fa-solid fa-database" />

	<DropdownNav title="Openstack" icon="fa-solid fa-cloud-arrow-down" href="#openstack">
		<NavOption href="/openstack" title="openstack" icon="fa-solid fa-house" />
		<NavOption href="/openstack/volumes" title="volumes" icon="fa-solid fa-box" />
		<NavOption href="/openstack/networks" title="networks" icon="fa-solid fa-wifi" />
	</DropdownNav>

	<DropdownNav title="Guacamole" icon="fa-solid fa-clapperboard" href="#guac">
		<NavOption href="/guacamole" title="guacamole" icon="fa-solid fa-house" />
		<NavOption href="/guacamole/topology" title="topology" icon="fa-solid fa-diagram-project" />
		<NavOption href="/guacamole/connections" title="connections" icon="fa-solid fa-plug" />
	</DropdownNav>

	<DropdownNav title="Saltstack" icon="fa-solid fa-computer" href="#saltstack">
		<NavOption title="jobs" href="/saltstack/jobs" icon="fa-solid fa-plug-circle-check" />
		<NavOption title="grains" href="/saltstack/grains" icon="fa-solid fa-wheat-awn" />
		<NavOption title="states" href="/saltstack/states" icon="fa-solid fa-cogs" />
	</DropdownNav>
</Navbar>

<main class="content" id="content" class:active={navOpen}>
	{@render children()}
</main>

<Notifications />

<style>
	#content {
		background-color: var(--dark-light);
		color: var(--white);
	}

	.content {
		padding: 20px;
		margin-left: 0;
		transition: all 0.3s;
	}

	.content.active {
		margin-left: 250px;
	}

	.overlay {
		pointer-events: none;
		position: fixed;
		width: 100%;
		height: 100%;
		z-index: 999;
		opacity: 0;
		transition: all 0.5s ease-in-out;
	}

	.overlay.open {
		pointer-events: all;
	}
</style>
