<script module>
	export { NavOption };
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';

	type NavbarProps = {
		active: boolean;
		children: Snippet;
	};

	let { active, children }: NavbarProps = $props();
</script>

{#snippet NavOption(title: string, href: string, icon: string)}
	<li class="nav-option-item" id="navigation-{title}">
		<a {href} class="option-anchor">
			<i class={icon}></i>
			{title}
		</a>
	</li>
{/snippet}

<nav id="sidebar" class="navigation sidebar" class:active>
	<ul class="navigation-menu sidebar-menu">
		{@render children()}
	</ul>
</nav>

<style lang="css">
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
