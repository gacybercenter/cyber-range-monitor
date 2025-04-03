<script lang="ts">
	import { getToasterState } from './toaster-state.svelte';
	import Toast from './Toast.svelte';

	/**
	 * Requires the context for the toaster to be set before
	 * the component is created.
	 */
	const toaster = getToasterState();
</script>

<section id="notifications">
	{#each toaster.toasts as toast}
		<Toast toast={toast.props} />
	{/each}
</section>

<style lang="css">
	section {
		position: fixed;
		bottom: 20px;
		right: 20px;
		z-index: 1050;
	}
</style>
