<script lang="ts">
	import type { Snippet } from 'svelte';

	type ActionCardProps = {
		title: string;
		summary?: string;
		icon: string;
		imageSrc: string;
		action: VoidFunction;
		children: Snippet;
	};

	/**
	 * title: string;
	 * description?: string;
	 * icon: string;
	 * imageSrc: string;
	 * children: Snippet - is in the body of the button
	 * --icon-color: string;
	 */
	let { title, summary, icon, imageSrc, children, action }: ActionCardProps = $props();
</script>

<div class="col-md col-md-6 col-lg-4 card-wrapper">
	<div class="action-card">
		<div class="card-header d-flex align-items-center">
			<i class="card-icon {icon} sm-orange"></i>
			<h5 class="card-title">{title}</h5>
		</div>

		<div class="card-thumbnail">
			<img src={imageSrc} class="card-img-top" alt="{title} Card thumbnail" />
		</div>

		<div class="card-body">
			{#if summary}<p class="card-text">{summary}</p>{/if}
			<button type="button" class="action-card-btn" onclick={action}>
				{@render children()}
			</button>
		</div>
	</div>
</div>

<style>
	.action-card {
		background-color: rgba(0, 0, 0, 0.2);
		border-radius: 8px;
		overflow: hidden;
		transition: all 0.3s ease;
		height: 100%;
		border: 1px solid rgba(255, 255, 255, 0.1);
	}

	.action-card:hover {
		transform: translateY(-2px);
		box-shadow: 0 10px 20px #fff;
		background-color: var(--black);
	}

	.action-card:hover .card-text,
	.action-card:hover .card-title {
		text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
	}

	.card-header {
		padding: 1rem;
		border-bottom: 2px solid white;
		background-color: rgba(0, 0, 0, 0.4);
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
	}

	.card-icon {
		font-size: 1.5rem;
		margin-right: 1rem;
		color: var(--icon-color, var(--accent-blue));
	}

	.card-title {
		margin: 0;
		font-weight: 600;
	}

	.card-thumbnail {
		position: relative;
		overflow: hidden;
		aspect-ratio: 16 / 9;
	}

	.card-img-top {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		transition: all 0.5s ease;
	}

	.action-card:hover .card-img-top {
		transform: scale(1.05);
	}

	.card-body {
		padding: 1.25rem;
	}

	.card-text {
		color: var(--cool-grey);
		margin-bottom: 1.5rem;
	}

	.action-card-btn {
		background-color: var(--accent-blue);
		border-color: var(--accent-blue);
		color: var(--white);
		border-radius: 4px;
		transition: all 0.3s ease;
		border: 2.5px solid var(--accent-blue);
		padding: 0.375rem 1.5rem;
		display: block;
		margin: 0 auto;
		width: fit-content;
	}

	.action-card-btn {
		background-color: var(--accent-grey);
		border-color: var(--accent-grey);
		transform: translateY(-4px);
		box-shadow: 0 4px 10px rgba(255, 255, 255, 0.2);
	}
</style>
