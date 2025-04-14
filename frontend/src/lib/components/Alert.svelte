<script lang="ts">
	import { capitialize } from './utils';

	type AlertProps = {
		message: string;
		type: 'info' | 'error';
	};

	let { message, type }: AlertProps = $props();

	let isInfo = $derived(type === 'info');

	let prev = $state(message);

	let dismissed = $state(false);

	$effect(() => {
		if (prev !== message) {
			dismissed = false;
			prev = message;
		}
	});

	const onclick = () => (dismissed = true);
</script>

<div
	class="alert {isInfo ? 'alert-success' : 'alert-danger'} d-flex align-items-center"
	role="alert"
	class:dismissed
>
	<button type="button" class="dismisser" {onclick} aria-label="Dismiss">
		<i class="{isInfo ? 'fa-solid fa-circle-info' : 'fa-solid fa-circle-xmark'} me-2"></i>
	</button>
	<strong class="alert-title me-1">{capitialize(type)}</strong>
	<span class="details">{message}</span>
</div>

<style>
	@keyframes fadeOut {
		from {
			opacity: 1;
			transform: translateY(0);
		}

		to {
			opacity: 0;
			transform: translateY(20px);
		}
	}

	.dismissed {
		animation: fadeOut 0.5s forwards;
	}

	.alert {
		color: white;
	}

	.alert-danger {
		background-color: var(--sm-orange);
	}

	.alert-success {
		background-color: var(--sm-green);
	}
</style>
