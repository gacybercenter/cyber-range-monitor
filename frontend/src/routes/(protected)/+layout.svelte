<script lang="ts">
	import Navigation from '$lib/components/navigation/Navigation.svelte';
	import AppHeader from '$lib/components/header/AppHeader.svelte';
	import { page } from '$app/state';

	import type { Snippet } from 'svelte';
	import type { LayoutData } from './$types';
	import { invalidateAll } from '$app/navigation';

	let { data, children }: { data: LayoutData; children: Snippet } = $props();

	const handleLogout = async () => {
		const res = await fetch('/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		if (res.redirected) {
			window.location.href = res.url;
			return;
		}
		await invalidateAll();
	};
	const { username, role } = data.user;

	const userProps = { username, role, onLogout: handleLogout };

	let navOpen = $state(false);
	const navToggleHandler = () => (navOpen = !navOpen);
</script>

<div class="overlay" role="none" class:open={navOpen} onclick={() => (navOpen = false)}></div>
<AppHeader user={userProps} pageName={page?.url.pathname} starCount={500} {navToggleHandler} />
<Navigation open={navOpen} />

<main class="content" id="content" class:active={navOpen}>
	{@render children()}
</main>

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
