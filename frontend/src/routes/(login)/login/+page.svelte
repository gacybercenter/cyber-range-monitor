<script lang="ts">
	import Starbackground from '$lib/components/header/Starbackground.svelte';
	import Alert from '$lib/components/common/Alert.svelte';

	import type { PageProps } from './$types';

	let { data, form }: PageProps = $props();
</script>

{#snippet formField(name: string, type: string, icon: string)}
	<div class="mb-4" id="{name}Field">
		<div class="input-group">
			<span class="input-group-text"><i class={icon}></i></span>
			<input {type} class="form-control" id={name} {name} placeholder={name} required />
		</div>
	</div>
{/snippet}

<section id="loginBody">
	<Starbackground starCount={1000} --star-bg-color="--cool-grey" />
	<div class="login-container">
		<div class="login-form">
			<div class="login-heading">
				<h1 class="login-title">
					Range Monitor
					<span class="hm-green">(v2)</span>
				</h1>
			</div>
			<form id="loginForm" method="POST">
				{@render formField('username', 'text', 'fa-solid fa-user')}
				{@render formField('password', 'text', 'fa-solid fa-lock')}
				<button type="submit" class="btn btn-login">
					<i class="fa-solid fa-right-to-bracket"></i>
					Login
				</button>
			</form>
			<div class="mb-6">
				{#if form?.message}
					<Alert title="Error" summary={form?.message || 'Could not sign in user'} type="danger" />
				{/if}
			</div>
		</div>
	</div>
</section>

<style>
	#loginBody {
		height: 100%;
		margin: 0;
		padding: 0;
		overflow: hidden;
		display: flex;
		justify-content: center;
		align-items: center;
		margin: 0;
		padding: 0;
		height: 100vh;
	}
	.login-container {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		width: 100%;
		z-index: 2;
	}

	.login-form {
		background-color: var(--black);
		border-radius: 8px;
		padding: 40px 50px;
		width: 100%;
		max-width: 420px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
		border: 1px solid rgba(255, 255, 255, 0.15);
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
	}

	.login-title {
		color: var(--white);
		font-size: 28px;
		font-weight: 600;
		text-align: center;
		margin-bottom: 35px;
	}

	.form-control,
	.input-group-text {
		background-color: var(--dark-light);
		border: 2px solid var(--white);
		color: var(--white);
		transition: all 0.3s ease;
	}

	.input-group-text {
		color: var(--cool-grey);
		background-color: rgba(0, 0, 0, 0.3);
		border-right: none;
	}

	.input-group .form-control {
		border-left: none;
	}

	.form-control:focus {
		color: var(--white);
	}

	.form-control::placeholder {
		color: var(--cool-grey);
		opacity: 0.7;
	}

	.btn-login {
		background-color: var(--accent-blue);
		border-color: var(--white);
		color: var(--white);
		font-weight: 500;
		padding: 12px 15px;
		width: 100%;
		margin-top: 20px;
		border-radius: 4px;
		transition: all 0.3s ease;
	}

	.btn-login:hover {
		background-color: #3c5c62;
		border-color: #3c5c62;
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
	}

	.input-group {
		position: relative;
		border-radius: 4px;
		overflow: hidden;
		box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
	}

	.form-check-input {
		background-color: var(--dark-light);
		border: 1px solid var(--cool-grey);
	}

	.form-check-input:checked {
		background-color: var(--accent-blue);
		border-color: var(--accent-blue);
	}
</style>
