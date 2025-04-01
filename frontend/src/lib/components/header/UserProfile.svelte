<script lang="ts">
	import { goto } from '$app/navigation';
	import { getNotificationState } from '../toasts/notification-state.svelte';
	import Spinner from '../Spinner.svelte';
	import { enhance } from '$app/forms';

	type UserProfileProps = {
		username: string;
		role: string;
		id: number;
	};

	let { username, role, id }: UserProfileProps = $props();

	let isSubmitting = $state(false);

	const notifier = getNotificationState();

	let icon = $derived(role === 'admin' ? 'fa-solid fa-user-tie' : 'fa-solid fa-circle-user');
	
</script>

<section class="col-auto" id="user-profile-{id}">
	<div class="user-container">
		<div class="user-info d-none d-md-block">
			<span class="user-name">{username}</span>
		</div>
		<div class="user-avatar me-2"><i class={icon}></i></div>
		<form
			action="?/logout"
			method="POST"
			use:enhance={() => {
				isSubmitting = true;
				notifier.create('Notice', 'Signing out...');
				return async ({ result }) => {
					if (result.type === 'redirect') {
						goto(result.location);
					}
					if (result.type === 'error') {
						getNotificationState().create('Error', result.error);
					}
				};
			}}
		>
			<button class="btn btn-primary btn-md" type="submit" disabled={isSubmitting}>
				<Spinner spinning={isSubmitting} spinText="Signing out...">
					<i class="fas fa-sign-out-alt"></i>
					<span class="d-md-inline">Logout</span>
				</Spinner>
			</button>
		</form>
	</div>
</section>

<style>
	.user-container {
		background-color: var(--dark);
		padding: 10px;
		border: 1px solid var(--white);
		display: flex;
		align-items: center;
		gap: 10px;
		z-index: 1000;
	}

	.user-container:hover {
		transform: translateY(-4px);
		box-shadow: 0 0 10px var(--white);
	}
	.user-name {
		font-weight: 600;
	}
	.user-avatar {
		width: 32px;
		height: 32px;
		border-radius: 50%;
		background-color: var(--accent-grey);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--white);
	}
</style>
