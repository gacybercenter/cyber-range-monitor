<script lang="ts">
	import UserProfile from './UserProfile.svelte';
	import Starbackground from '../starbackground/Starbackground.svelte';
	import type { UserResponse } from '$lib/api/client';
	import Breadcrumbs from './Breadcrumbs.svelte';

	type HeaderProps = {
		starCount?: number;
		onclick: VoidFunction;
		user: UserResponse;
		isOpen: boolean;
	};

	let { starCount = 50, user, onclick, isOpen }: HeaderProps = $props();

	const OPEN_ICON = 'fas fa-bars fa-lg';
	const CLOSE_ICON = 'fa-solid fa-x';
</script>

{#snippet navToggler()}
	<button
		type="button"
		id="navToggler"
		{onclick}
		class:open={isOpen}
		class="btn btn-link-lg text-white"
		aria-label="Hamburger Menu toggle"
		onkeydown={(e) => (e.key === 'Enter' ? onclick() : null)}
		tabindex="0"
	>
		<i class={!isOpen ? OPEN_ICON : CLOSE_ICON}></i>
	</button>
{/snippet}

<section id="app-header" class="header">
	<Starbackground {starCount} />
	<div class="container-fluid">
		<header class="row align-items-center" id="headerContent">
			<div class="col-auto" id="navToggle">
				{@render navToggler()}
			</div>
			<div class="col" id="branding">
				<h4 class="mb-0">
					Range Monitor <span class="hm-green">(v2)</span>
				</h4>
				<Breadcrumbs />
			</div>
			<UserProfile {...user} />
		</header>
	</div>
</section>

<style>
	.header {
		background-color: var(--black);
		padding: 15px 20px;
		position: relative;
		overflow: hidden;
		border-bottom: 1px solid var(--accent-blue);
		border-radius: 0 0 8px 8px;
		color: var(--white);
	}

	#navToggler:focus {
		border: 2.5px solid var(--cool-grey);
	}

	#navToggler:hover {
		transform: scale(1.05);
	}

	#navToggler.open i:hover {
		color: red;
	}
</style>
