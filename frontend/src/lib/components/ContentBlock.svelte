<script lang="ts">
	let { children } = $props();
</script>

<div class="centered-content-container">
	<div class="centered-content-block">
		{@render children()}
	</div>
</div>

<style lang="css">
	.centered-content-container {
		display: flex;
		justify-content: center;
		align-items: center;
		min-height: 300px;
		margin: 30px 0;
	}

	.centered-content-block {
		background-color: var(--black);
		border-radius: 8px;
		padding: 30px;
		width: 100%;
		max-width: 800px;
		border: 1px solid rgba(255, 255, 255, 0.1);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
		position: relative;
		overflow: hidden;
	}
</style>
