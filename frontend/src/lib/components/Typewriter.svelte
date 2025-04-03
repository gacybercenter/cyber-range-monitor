<script lang="ts">
	type TypewriterProps = {
		messages: string[];
		speed?: number;
		delay?: number;
		onComplete?: () => void;
		textClass?: string;
	};

	/**
	 * messages: string[];
	 * speed: number;
	 * delay: number;
	 * --line-height: number;
	 */
	let { messages, speed = 50, delay = 2500, onComplete, textClass }: TypewriterProps = $props();

	let index = $state(0);
	let showCursor = $state(true);
	let text = $state('');

	let currentWord = $derived(messages[index]);

	$effect(() => {
		if (index >= messages.length) {
			showCursor = false;
			onComplete && onComplete();
			return;
		}
		text = '';
		let chardex = -1;
		let delayId: number | null = null;

		let typeInterval = setInterval(() => {
			if (++chardex < currentWord.length) {
				text += currentWord[chardex];
			} else {
				clearInterval(typeInterval);
				delayId = setTimeout(() => {
					showCursor = false;
					index++;
				}, delay);
			}
		}, speed);

		return () => {
			clearInterval(typeInterval);
			if (delayId) {
				clearTimeout(delayId);
			}
		};
	});
</script>

<p class="typewriter-content d-inline-block {textClass ?? ''}">
	<span class="typed-text">
		{text}
	</span>
	<span class="cursor d-inline-block" class:hide={!showCursor}>|</span>
</p>

<style>
	.typewriter-content {
		display: inline-block;
		line-height: var(--line-height, 1.2);
	}

	.typed-text {
		white-space: pre-wrap;
	}

	.cursor {
		display: inline-block;
		position: relative;
		font-weight: bold;
		color: var(--cursor-color, #fff);
		margin-left: 2px;
		animation: cursor-blink 1s step-end infinite;
	}

	.cursor {
		display: inline-block;
		font-weight: bold;
		animation: cursor-blink 0.8s infinite;
	}

	.cursor.hide {
		opacity: 0;
	}

	@keyframes cursor-blink {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0;
		}
	}
</style>
