<script lang="ts">
	let { title, icon, href, children } = $props();
	let open = $state(true);

	const dropdownClick = (e: MouseEvent) => {
		e.preventDefault();
		open = !open;
	};
</script>

<li class="nav-option-item drop-option" class:open id="navOptionDropdown-{title}">
	<a
		{href}
		class="menu-toggle option-anchor"
		onclick={dropdownClick}
		aria-haspopup="true"
		aria-expanded={open}
		class:open
	>
		<i class={icon}></i>
		{title}
		<i class="fas fa-chevron-right chevron" class:rotated={open}></i>
	</a>
	<ul class="submenu" class:show={open}>
		{@render children()}
	</ul>
</li>

<style>
	.rotated {
		transform: rotate(90deg);
	}

	.menu-toggle {
		transition: transform 0.3s ease-out;
	}

	.menu-toggle.open {
		border: 0.5px solid var(--cool-grey);
	}
</style>
