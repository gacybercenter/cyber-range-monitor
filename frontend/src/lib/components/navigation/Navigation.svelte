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

	let { menuOptions, open, closeBtnClicked }: NavigationProps = $props();
</script>

<nav id="sidebar" class="navigation sidebar" class:active={open}>
	<section class="sidebar-header navigation-header">
		<h5 class="m-0">Range Monitor <span class="hm-green">(v2)</span></h5>
		<button
			id="navCloseBtn"
			class="btn-close btn-close-white"
			aria-label="Toggle sidebar"
			onclick={closeBtnClicked}
		></button>
	</section>
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
		top: 0;
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

	.navigation-header {
		padding: 20px;
		background-color: var(--accent-blue);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.navigation-menu {
		padding: 0;
		list-style: none;
		margin: 0;
	}

	.navigation-menu :global(.nav-option-item) {
		border-bottom: 1px solid rgba(255, 255, 255, 0.05);
	}

	.navigation-menu :global(.option-anchor) {
		padding: 12px 20px;
		display: flex;
		align-items: center;
		color: var(--cool-grey);
		text-decoration: none;
		transition: all 0.3s ease;
		gap: 10px;
	}

	.navigation-menu :global(.option-anchor:hover) {
		background-color: rgba(255, 255, 255, 0.05);
		color: var(--white);
		border: 2.5px solid var(--accent-gray);
		border-radius: 5px;
	}

	.navigation-menu :global(.option-anchor i:first-child) {
		width: 20px;
		text-align: center;
	}

	.navigation-menu :global(.menu-toggle .chevron) {
		margin-left: auto;
		transition: transform 0.3s ease;
	}

	.navigation-menu :global(.submenu) {
		list-style: none;
		padding-left: 0;
		max-height: 0;
		overflow: hidden;
		transition: max-height 0.3s ease-out;
		background-color: rgba(0, 0, 0, 0.2);
		margin: 0;
	}

	.navigation-menu :global(.submenu.show) {
		max-height: 500px;
	}

	.navigation-menu :global(.option-anchor) {
		padding-left: 50px;
		font-size: 0.9em;
	}
</style>
