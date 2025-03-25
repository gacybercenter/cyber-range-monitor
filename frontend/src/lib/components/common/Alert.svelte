<script lang="ts">
	import type { AlertProps } from './common.types';

	let { title, summary, type }: AlertProps = $props();

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
</script>

<div class="alert-{type} alert-dismissible alert fade show" role="alert">
	<strong class="alert-title">
		<i class={getAlertIcon()}></i>
		{title}
	</strong>
	{summary}
	<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>

<style>
	.alert-title i {
		margin-right: 5px;
	}
</style>
