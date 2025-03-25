<script lang="ts">
	import '../app.css';
	import 'bootstrap/dist/css/bootstrap.min.css';

	import Navigation, { navDropdown, navOption } from '$lib/components/navigation/Navigation.svelte';
	import AppHeader from '$lib/components/header/AppHeader.svelte';

	import { page } from '$app/state';

	let { children } = $props();

	const homeOption = (href: string) => navOption('home', href, 'fa-solid fa-house');

	const guacOptions = [
		homeOption('/guacamole'),
		navOption('connections', '/guacamole/connections', 'fa-solid fa-plug'),
		navOption('users', '/guacamole/topology', 'fa-solid fa-hexagon-nodes')
	];

	const openstackOptions = [
		homeOption('/openstack'),
		navOption('volumes', '/openstack/volumes', 'bi bi-hdd-stack'),
		navOption('networks', '/openstack/networks', 'bi bi-wifi')
	];

	const saltstackOptions = [
		homeOption('/saltstack'),
		navOption('jobs', '/saltstack/jobs', 'bi bi-clipboard-data'),
		navOption('grains', '/saltstack/grains', 'bi bi-box2'),
		navOption('states', '/saltstack/states', 'bi bi-file-earmark-code')
	];

	const navigation = [
		homeOption('/'),
		navOption('users', '/users', 'fa-regular fa-circle-user'),
		navOption('datasources', '/datasources', 'fa-solid fa-database'),
		navDropdown('openstack', '/openstack', 'fa-solid fa-cloud-arrow-down', openstackOptions),
		navDropdown('guacamole', '/guacamole', 'fa-solid fa-clapperboard', guacOptions),
		navDropdown('saltstack', '/saltstack', 'bi bi-bounding-box', saltstackOptions)
	];

	const onLogout = () => alert('logged out');

	const user = {
		username: 'foo',
		role: 'bar',
		onLogout
	};

	let navOpen = $state(false);

	const toggleNav = () => (navOpen = !navOpen);
</script>

<Navigation menuOptions={navigation} open={navOpen} closeBtnClicked={() => (navOpen = false)} />
<!-- 
	svelte-ignore a11y_click_events_have_key_events 
-->
<div class="overlay" onclick={() => (navOpen = false)} role="none" class:active={navOpen}></div>

<AppHeader
	{user}
	pageName={page?.url.pathname}
	starCount={100}
	menuOpenBtnClick={() => (navOpen = true)}
/>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
<main class="content" id="content" class:active={navOpen}>
	{@render children()}
</main>

<style>
	.content {
		padding: 20px;
		margin-left: 0;
		transition: all 0.3s;
	}

	.content.active {
		margin-left: 250px;
	}

	.overlay {
		display: none;
		position: fixed;
		width: 100%;
		height: 100%;
		background: rgba(0, 0, 0, 0.7);
		z-index: 999;
		opacity: 0;
		transition: all 0.5s ease-in-out;
	}

	.overlay.active {
		display: block;
		opacity: 1;
	}
</style>
