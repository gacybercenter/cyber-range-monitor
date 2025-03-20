<script module>
	type Option = {
		name: string;
		link: string;
		icon: string;
	};

	export interface NavOptionProps {
		name: string;
		icon: string;
		link: string;
		collapse?: boolean;
		options?: Option[];
	}
</script>

<script lang="ts">
	let { name, link = '', icon = '', collapse = false, options }: NavOptionProps = $props();

	let isOpen = $state(false);
</script>

<li class="nav-item me-3">
	{#if collapse && options && options.length > 0}
		<div class="collapsible-menu">
			<button
				class="btn btn-primary"
				aria-expanded={isOpen}
				aria-controls="collapsible-content"
				onmouseenter={() => (isOpen = true)}
				onmouseleave={() => (isOpen = false)}
			>
				{name} <i class="bi bi-chevron-down" class:rotate={isOpen}></i>
			</button>
			<div class="collapsible-content" class:show={isOpen} id="collapsible-content">
				{#each options as opt}
					<a 
						href={opt.link} 
						class="sub-opt d-block px-3 py-2 text-decoration-none btn-primary"
					>
						{opt.name} <i class={opt.icon}></i>
					</a>
				{/each}
			</div>
		</div>
	{:else}
		<a href={link} class="btn btn-primary">
			{name} <i class={icon}></i>
		</a>
	{/if}
</li>

<style>
	.collapsible-content {
		display: none;
		position: absolute;
		background-color: var(--white);
		min-width: 160px;
		box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.2);
		z-index: 1;
		border-radius: 4px;
	}

	.collapsible-menu:hover .collapsible-content,
	.collapsible-content.show {
		display: block;
	}

	.rotate {
		transform: rotate(180deg);
		transition: transform 0.2s ease-in-out;
	}

	.collapsible-content a {
		color: var(--primary);
		transition: background-color 0.2s ease;
	}

	.collapsible-content a:hover {
		background-color: rgba(0, 0, 0, 0.05);
		color: var(--accent-blue);
	}

	
</style>
