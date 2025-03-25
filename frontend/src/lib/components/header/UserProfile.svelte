<script lang="ts">
	import type { UserProfileProps } from '../common/common.types';

	let { username, role, onLogout }: UserProfileProps = $props();
</script>

{#snippet userIcon()}
	{#if role === 'admin'}
		<i class="fa-solid fa-user-tie"></i>
	{:else}
		<i class="fa-solid fa-circle-user"></i>
	{/if}
{/snippet}

<div class="col-auto">
	<div class="user-container">
		<div class="user-info d-none d-md-block">
			<span class="user-name">{username}</span>
		</div>
		<div class="user-avatar">
			{@render userIcon()}
		</div>
		<button class="btn btn-primary btn-sm" onclick={onLogout}>
			<i class="fas fa-sign-out-alt"></i>
			<span class="d-none d-md-inline">Logout</span>
		</button>
	</div>
</div>

<style>
	.user-container {
		background-color: var(--dark-light);
		padding: 10px;
		border: 1px solid var(--accent-blue);
		box-shadow: 0 0 5px rgba(0, 0, 0, 0.2);
		display: flex;
		align-items: center;
		gap: 10px;
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
