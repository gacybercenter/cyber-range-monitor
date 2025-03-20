<script module>
	import type { NavOptionProps } from './NavOption.svelte';

	export interface HeaderProps {
		pageName: string;
		navOptions: NavOptionProps[];
		user: {
			username: string;
			role: string;
		};
	}
</script>

<script lang="ts">
	import Navigation from './Navigation.svelte';
	import Profile from './Profile.svelte';

	const DEFAULT_NAVIGATION: NavOptionProps[] = [
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

	let { pageName, navOptions = DEFAULT_NAVIGATION, user }: HeaderProps = $props();

	let isScrolling = $state(false);

	$effect(() => {
		const handleScroll = () => {
			isScrolling = window.scrollY > 10;
		};
		window.addEventListener('scroll', handleScroll);
		return () => window.removeEventListener('scroll', handleScroll);
	});
</script>

<header class="site-header" class:scrolled={isScrolling}>
	<div class="container">
		<div class="header-container">
			<div class="header-title">
				<h1 class="h4 mb-0">{pageName}</h1>
			</div>

			<div class="header-navigation">
				<div class="col-md-8">
					<Navigation {navOptions} />
				</div>
				<div class="header-profile">
					<Profile {...user} />
				</div>
			</div>
		</div>
	</div>
</header>

<style>
	.site-header {
		border-bottom: 1px solid var(--hm-green);
		padding: 15px 0;
		background-color: var(--primary);
		transition: all 0.3s ease;
	}

	.site-header.scrolled {
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
	}

	.header-container {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.header-title {
		flex: 0 0 auto;
	}

	.header-navigation {
		flex: 1 1 auto;
		display: flex;
		justify-content: center;
	}

	.header-profile {
		flex: 0 0 auto;
	}
</style>
