<script lang="ts">
	import type { ToastProps } from './toast.types';

	const DEFAULT_ICON = 'fa-solid fa-bell';

	const getPreset = (preset?: string) => (preset ? 'toast-' + preset : 'toast-primary');

	let { toast }: { toast: ToastProps } = $props();
</script>

<section class="toast-notification {getPreset(toast.options?.preset)}">
	<div class="toast-header">
		<i class="toast-icon {toast.options?.icon || DEFAULT_ICON}"></i>
		<strong class="toast-title">{toast.title}</strong>
	</div>
	<div class="toast-body">{toast.message}</div>
</section>

<style>
	.toast-notification {
		background-color: rgba(33, 37, 41, 0.95);
		color: var(--white);
		border-radius: 4px;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		overflow: hidden;
		min-width: 300px;
		margin-bottom: 0.75rem;
		transform: translateY(20px);
		transition: all 0.3s ease;
		border: 1px solid var(--accent-grey);
	}

	.toast-header {
		display: flex;
		align-items: center;
		padding: 0.5rem 0.75rem;
		border-bottom: 1px solid var(--accent-grey);
		background-color: transparent;
	}

	i {
		margin-right: 0.75rem;
		font-size: 1.25rem;
	}

	strong {
		font-weight: 600;
		flex-grow: 1;
	}

	.toast-body {
		padding: 0.75rem;
	}

	.toast-primary i {
		color: var(--accent-blue);
	}

	.toast-success i {
		color: var(--hm-green);
	}

	.toast-danger i {
		color: var(--sm-orange);
	}

	.toast-secondary .toast-header {
		color: var(--white);
		background-color: var(--accent-grey);
	}
</style>
