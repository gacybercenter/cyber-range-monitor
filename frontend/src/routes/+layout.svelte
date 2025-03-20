<script lang="ts">
	import '../app.css';
	import Header from '$lib/components/Header.svelte';

	let { children } = $props<{ children: any }>();

	let pageName = $state('Home');

	const navOptions = [
		{ name: 'home', link: '/', icon: 'bi bi-house' },
		{
			name: 'datasources',
			link: '',
			icon: '',
			collapse: true,
			options: [
				{ name: 'Openstack', link: '/datasource/openstack', icon: 'bi bi-cloud' },
				{ name: 'Guacamole', link: '/datasource/guacamole', icon: 'bi bi-camera' },
				{ name: 'Saltstack', link: '/datasources/saltstack', icon: 'bi bi-bell-slash' }
			]
		},
		{ name: 'users', link: '/users', icon: 'bi-person-circle' },
		{ name: 'openstack', link: '/openstack', icon: 'bi bi-cloud' },
		{ name: 'guacamole', link: '/guacamole', icon: 'bi bi-camera' },
		{ name: 'saltstack', link: '/saltstack', icon: 'bi bi-bell-slash' }
	];

	const user = {
		username: 'foo',
		role: 'bar'
	};
</script>

<div id="app-container">
	<Header {pageName} {navOptions} {user} />
	<main class="container py-4">
		{@render children()}
	</main>
</div>

<style>
	#app-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	main {
		flex: 1;
	}
</style>
