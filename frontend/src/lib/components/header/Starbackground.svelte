<script lang="ts">
	import type { StarbackgroundProps } from './header.types';

	let { starCount }: StarbackgroundProps = $props();

	type StarConfig = {
		left: number;
		top: number;
		size: number;
		delay: number;
	};

	const createStar = (): StarConfig => {
		const left = Math.floor(Math.random() * 100);
		const top = Math.floor(Math.random() * 100);
		const size = Math.floor(Math.random() * 3) + 1;
		const delay = Math.random() * 15;

		return { left, top, size, delay };
	};

	const stars = Array.from({ length: starCount }, createStar);
</script>

<section class="stars" role="presentation" aria-hidden="true">
	{#each stars as { left, top, size, delay }}
		<div
			class="star"
			style="
				left: {left}%;
				top: {top}%; 
				width: {size}px;
				height: {size}px;
				animation-delay: {delay}s;
			"
		></div>
	{/each}
</section>

<style>
	.stars {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
	}

	.star {
		position: absolute;
		background-color: var(--white);
		width: 2px;
		height: 2px;
		border-radius: 50%;
		opacity: 0.5;
		animation: float 15s linear infinite;
	}

	@keyframes float {
		0% {
			transform: translateY(0) translateX(0);
			opacity: 0;
		}
		10% {
			opacity: 1;
		}
		90% {
			opacity: 1;
		}
		100% {
			transform: translateY(-20px) translateX(20px);
			opacity: 0;
		}
	}
</style>
