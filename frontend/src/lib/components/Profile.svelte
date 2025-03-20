<script module>
	export interface ProfileProps {
		username: string;
		role: string;
	}
</script>

<script lang="ts">
	let { username = 'Admin', role = 'admin' }: ProfileProps = $props();
</script>

<div class="user-container ms-auto">
	<div class="user-icon">
		<i class="bi-person-circle"></i>
	</div>
	<div class="user-info">
		<span class="user-name">{username}</span>
		<span class="user-role">{role}</span>
	</div>
	<button class="logout-btn ms-3" onclick={() => alert('Logout clicked!')}>
		<i class="bi bi-box-arrow-right me-1"></i> Logout
	</button>
</div>

<style>
	.user-container {
		display: flex;
		align-items: center;
		gap: 10px;
		border-radius: 5px;
		background-color: rgba(154, 155, 157, 0.1);
		max-width: fit-content;
		color: var(--accent-grey);
	}

	.user-icon {
		font-size: 1.5rem;
		color: var(--accent-gray);
	}

	.user-info {
		display: flex;
		flex-direction: column;
	}

	.user-name {
		font-weight: 600;
		font-size: 0.9rem;
	}

	.user-role {
		font-size: 0.8rem;
	}

	.logout-btn {
		color: var(--sm-orange);
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.9rem;
		font-weight: 500;
		transition: color 0.2s ease;
	}

	.logout-btn:hover {
		text-decoration: underline;
		color: var(--primary);
	}
</style>
