<script lang="ts">
	import { page } from '$app/state';

	const createCrumb = (path: string, absPath: string, current: string) => {
		const label = path.replace(/-/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
		return {
			label,
			href: absPath,
			active: current === absPath
		};
	};

	let breadcrumbs = $derived.by(() => {
		const paths = page.url.pathname.split('/').filter(Boolean);
		const currentPage = page.url.pathname;
		const crumbs = [
			{
				label: 'Home',
				href: '/',
				active: currentPage === '/'
			}
		];

		let absPath = '';
		paths.forEach((path) => {
			absPath += `/${path}`;
			crumbs.push(createCrumb(path, absPath, currentPage));
		});

		return crumbs;
	});
</script>

<nav aria-label="breadcrumb">
	<ol class="breadcrumb">
		{#each breadcrumbs as { label, href, active }: Breadcrumbs}
			<li class="breadcrumb-item" class:active>
				{#if active}
					{label}
				{:else}
					<a {href}>{label}</a>
				{/if}
			</li>
		{/each}
	</ol>
</nav>

<style>
	.breadcrumb {
		background-color: transparent;
		margin-bottom: 0;
		padding: 0;
	}

	.breadcrumb-item,
	.breadcrumb-item a {
		color: var(--cool-grey);
	}

	.breadcrumb-item.active {
		color: var(--accent-blue);
	}
</style>
