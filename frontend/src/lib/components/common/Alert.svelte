<script lang="ts">
	type AlertProps = {
		title: string;
		message: string;
		type: 'warning' | 'danger' | 'success';
		icon?: string;
	};

	const getAlertIcon = () => {
		switch (type) {
			case 'success':
				return 'fas fa-check-circle';
			case 'danger':
				return 'fa-solid fa-circle-exclamation';
			case 'warning':
				return 'fas fa-info-circle';
			default:
				return 'fas fa-bell';
		}
	};

	let { title, message, type, icon = getAlertIcon() }: AlertProps = $props();
	let id = $derived(`alert-${type}-${title}`);
</script>

<div
	class="alert alert-{type} alert-dismissible d-flex align-items-center fade show"
	role="alert"
	{id}
>
	<i class="{icon} me-2"></i>
	<strong class="alert-title me-1">{title}</strong>
	<span class="details">{message}</span>
	<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>

<style>
	.alert {
		color: white;
	}

	.alert-danger {
		background-color: var(--sm-orange);
	}

	.alert-warning {
		background-color: var(--hm-green);
	}

	.alert-success {
		background-color: var(--accent-blue);
	}
</style>
