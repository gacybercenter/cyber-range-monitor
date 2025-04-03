<script lang="ts">
	import type { Snippet } from 'svelte';

	type SpinnerProps = {
		spinning: boolean;
		spinText?: string;
		children: Snippet;
	};

	/**
	 * Displays a spinner when spinning is set to true
	 * otherwise, the children of the component are rendered
	 */
	let { spinning, spinText, children }: SpinnerProps = $props();
</script>

{#if spinning}
	<span
		class="spinner-border spinner-border-sm me-2 text-light"
		role="status"
		aria-hidden={spinning}
	></span>
	{spinText}
{:else}
	{@render children()}
{/if}

<style lang="css">
</style>
