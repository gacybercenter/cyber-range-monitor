<script lang="ts">
	import { createStar, moveAndTwinkleStar, type Star } from './star-utils';

	/**
	 * Starbackground
	 * starCount: number;
	 * --star-bg: (default: --black);
	 */

	let { starCount }: { starCount: number } = $props();

	let stars = $derived<Star[]>(Array.from({ length: starCount }, createStar));

	let canvas: HTMLCanvasElement;
	let ctx: CanvasRenderingContext2D | null;
	let width = 0;
	let height = 0;
	let animationFrame: number;

	const resize = () => {
		if (!canvas) return;

		const rect = canvas.parentElement?.getBoundingClientRect();

		if (!rect) return;

		width = rect.width;
		height = rect.height;
		canvas.width = width;
		canvas.height = height;
	};

	$effect(() => {
		if (!canvas) return;

		ctx = canvas.getContext('2d');
		resize();

		const resizeObserver = new ResizeObserver(() => resize());

		resizeObserver.observe(canvas.parentElement as Element);

		const animate = (time: number) => {
			if (!ctx) return;

			ctx.clearRect(0, 0, width, height);

			stars.forEach((star, index) => {
				if (time / 1000 < star.delay || !ctx) return;

				star.progress += star.speed;
				if (star.progress > 1) {
					stars[index] = createStar();
					return;
				}

				const { x, y, radius, opacity } = moveAndTwinkleStar(star, width, height);

				ctx.fillStyle = `rgba(255, 255, 255, ${opacity})`;
				ctx.beginPath();
				ctx.arc(x, y, radius, 0, Math.PI * 2);
				ctx.fill();
			});

			animationFrame = requestAnimationFrame(animate);
		};

		animationFrame = requestAnimationFrame(animate);

		return () => {
			cancelAnimationFrame(animationFrame);
			resizeObserver.disconnect();
		};
	});
</script>

<section class="stars" role="presentation" aria-hidden="true">
	<canvas bind:this={canvas} class="star-background"></canvas>
</section>

<style>
	.stars {
		background-color: var(--star-bg, --black);
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
	}

	canvas {
		width: 100%;
		height: 100%;
	}
</style>
