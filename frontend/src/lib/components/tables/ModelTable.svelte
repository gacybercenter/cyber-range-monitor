<script lang="ts">
	import type { Snippet } from 'svelte';
	import TableToolBar from './TableToolBar.svelte';
	import type { TableToolBarProps } from './table.types';

	type ModelTableProps = {
		toolbar: TableToolBarProps;
		header: Snippet;
		children: Snippet;
		onCreate: () => void;
	};

	let { toolbar, header, children, onCreate }: ModelTableProps = $props();
</script>

<div class="card">
	<div class="card-body postion-relative">
		<TableToolBar {...toolbar} />

		<div class="table-responsive">
			<table class="table table-hover">
				<thead>
					{@render header()}
				</thead>
				<tbody>
					{@render children()}
				</tbody>
			</table>
		</div>
	</div>

	<div class="d-flex justify-content-center mt-4">
		<button class="btn btn-primary px-4 py2 create-btn" onclick={onCreate}>
			<i class="fa-solid fa-plus me-2"></i> Create
		</button>
	</div>
</div>

<style>
	.create-btn {
		transition: all 0.3s ease;
	}

	.create-btn:hover {
		background-color: var(--hm-green);
		font-weight: bolder;
		border-radius: 5px;
	}

  table {
    color: white;
  }






</style>
