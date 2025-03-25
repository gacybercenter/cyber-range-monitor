<script module>
	export const navOption = (title: string, href: string, icon: string): NavButtonProps => {
		return { title, href, icon } as NavButtonProps;
	};

	export const navDropdown = (
		title: string,
		href: string,
		icon: string,
		subOptions: NavButtonProps[]
	): NavButtonProps => {
		return { title, href, icon, subOptions } as NavButtonProps;
	};
</script>

<script lang="ts">
	import type { NavButtonProps, NavigationProps } from './navigation.types';
	import DropdownNav from './DropdownNav.svelte';
	import NavOption from './NavOption.svelte';

	let { menuOptions, open }: NavigationProps = $props();
</script>

<nav id="sidebar" class="navigation sidebar" class:active={open}>
	<ul class="navigation-menu sidebar-menu">
		{#each menuOptions as option}
			<!-- 
			 	would do spread assignment, but the shared interface has a
			 	possibly undefined prop which would cause issues passing to component
			 -->
			{#if option.subOptions && option.subOptions.length > 0}
				<DropdownNav
					href={option.href}
					title={option.title}
					icon={option.icon}
					subOptions={option.subOptions}
				/>
			{:else}
				<NavOption href={option.href} title={option.title} icon={option.icon} />
			{/if}
		{/each}
	</ul>
</nav>

<style>
	.navigation {
		background-color: var(--black);
		width: 250px;
		position: fixed;
		left: -250px;
		height: 100%;
		z-index: 1000;
		transition: all 0.3s;
		overflow-y: auto;
		border-right: 1px solid var(--accent-blue);
	}

	.navigation.active {
		left: 0;
	}

	.navigation-menu {
		padding: 0;
		list-style: none;
		margin: 0;
	}
</style>
