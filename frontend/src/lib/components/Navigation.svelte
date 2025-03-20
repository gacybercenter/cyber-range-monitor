<script lang="ts">
	import NavOption from './NavOption.svelte';
	import type { NavOptionProps } from './NavOption.svelte';

	let { navOptions } = $props<{ navOptions: NavOptionProps[] }>();
</script>

<nav class="navigation">
	<ul class="nav-list">
		{#each navOptions as option}
			<NavOption {...option} />
		{/each}
	</ul>
</nav>

<style>
	.navigation {
		width: 100%;
		display: flex;
		justify-content: center;
	}

	.nav-list {
		list-style: none;
		display: flex;
		padding: 0;
		justify-content: center;
	}
</style>
