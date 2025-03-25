<script lang="ts">
	import type { DropdownNavProps } from './navigation.types';
	import NavOption from './NavOption.svelte';

	let { title, icon, href, subOptions }: DropdownNavProps = $props();
	let open = $state(false);

	const dropdownClick = (e: MouseEvent) => {
		e.preventDefault();
		open = !open;
	};
	
</script>

<!-- need to add "show" -->
<li class="nav-option-item" id="navOptionDropdown-{title}">
	<a {href} class="menu-toggle" onclick={dropdownClick} aria-haspopup="true" aria-expanded={open}>
		<i class={icon}></i>
		{title}
		<i class="fas fa-chevron-right chevron"></i>
	</a>
	<ul class="submenu" class:show={open}>
		{#each subOptions as subOption}
			<NavOption {...subOption} />
		{/each}
	</ul>
</li>
