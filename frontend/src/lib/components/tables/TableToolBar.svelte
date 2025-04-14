<script lang="ts">
	import Spinner from '../Spinner.svelte';
	import type { TableToolBarProps } from './table.types';

	let { onChange, onRefresh, title }: TableToolBarProps = $props();

	let searched = $state<string>('');

	let isRefreshing = $state(false);
</script>

<section class="table-tool-bar d-flex align-items-center justify-content-between">
	<h2 class="toolbar-title">{title}</h2>
	<div class="search-container">
		<i class="fas fa-search search-icon"></i>
		<input
			type="text"
			id="searchInput"
			class="form-control"
			placeholder="Search for"
			bind:value={searched}
			oninput={() => onChange(searched)}
		/>
		<button
			class="clear-btn"
			id="clearSearch"
			onclick={() => (searched = '')}
			aria-label="Clear search"
		>
			<i class="fas fa-times"></i>
		</button>
	</div>
	<button
		class="btn btn-primary"
		onclick={async () => {
			isRefreshing = true;
			await onRefresh();
			isRefreshing = false;
		}}
		disabled={isRefreshing}
	>
		<Spinner spinText="Refreshing..." spinning={isRefreshing}>
			<i class="fas fa-sync-alt me-2"></i> Refresh
		</Spinner>
	</button>
</section>

<style>
	.toolbar-title {
		font-size: 1.6rem;
		font-weight: 500;
		margin: 0;
		color: white;
	}

	.table-tool-bar {
		/* display: flex;
		justify-content: space-between;
		align-items: center; */
		margin-bottom: 1.5rem;
		padding-top: 2rem;
	}

	.search-container {
		position: relative;
		flex: 1;
		max-width: 400px;
	}

	.search-icon {
		position: absolute;
		left: 14px;
		top: 50%;
		transform: translateY(-50%);
		color: var(--cool-grey);
	}

	.clear-btn {
		position: absolute;
		right: 10px;
		top: 50%;
		transform: translateY(-50%);
		border: none;
		background: transparent;
		color: var(--cool-grey);
		padding: 0;
		cursor: pointer;
	}

	.clear-btn:hover {
		color: var(--white);
	}

	@media (max-width: 992px) {
		.search-container {
			max-width: none;
		}
	}
</style>
