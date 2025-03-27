<script lang="ts">
	import type { StatCardProps } from './common.types';

	let { title, badgeIcon, value, description }: StatCardProps = $props();
</script>

<section class="col-12 col-md-6 col-lg-3 mb-4" id="statCard-{title}">
	<div class="stats-card">
		<div class="stats-card-header">
			<div class="stats-card-icon">
				<i class="{badgeIcon} fa-lg text-white"></i>
			</div>
			<div>
				<h2 class="stats-card-value">{value}</h2>
				<p class="stats-card-title">{title}</p>
			</div>
		</div>
		<p class="stats-card-text">{description}</p>
	</div>
</section>

<style>
	.stats-card {
		background-color: var(--black);
		border-radius: 8px;
		padding: 15px;
		height: 100%;
		display: flex;
		flex-direction: column;
		color: white;
		transition: all 0.3s ease;
	}

	.stats-card-header {
		display: flex;
		align-items: center;
		margin-bottom: 15px;
	}

	.stats-card-icon {
		width: 44px;
		height: 44px;
		border-radius: 8px;
		display: flex;
		align-items: center;
		justify-content: center;
		margin-right: 15px;
		flex-shrink: 0;
		background-color: var(--badge-color);
	}

	.stats-card-value {
		font-size: 32px;
		font-weight: 600;
		color: var(--white);
		margin: 0;
		line-height: 1.2;
	}

	.stats-card-title {
		color: var(--cool-grey);
		margin: 0;
		font-size: 14px;
	}

	.stats-card-text {
		color: var(--white);
		margin-top: 5px;
		font-size: 14px;
	}

	.stats-card:hover {
		transform: translateY(-3px);
		box-shadow: 0 5px 15px rgba(255, 255, 255, 0.2);
	}
</style>
