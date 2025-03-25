<script lang="ts">
	import UserProfile from './UserProfile.svelte';
	import Starbackground from './Starbackground.svelte';

	import type { AppHeaderProps } from './header.types';

	let { pageName, user, menuOpenBtnClick, starCount = 50 }: AppHeaderProps = $props();
</script>

<header id="appHeader" class="header">
	<Starbackground {starCount} />
	<div class="container-fluid">
		<section class="row align-items-center" id="headerContent">
			<div class="col-auto" id="navToggle">
				<button
					type="button"
					id="sidebarCollapse"
					class="btn btn-link text-white p-0"
					aria-label="Hamburger Menu toggle"
					onclick={menuOpenBtnClick}
					onkeydown={(e) => (e.key === 'Enter' ? menuOpenBtnClick() : null)}
					tabindex="0"
				>
					<i class="fas fa-bars fa-lg"></i>
				</button>
			</div>
			<div class="col" id="pageHeading">
				<h4 class="mb-0">
					Range Monitor
					<span class="hm-green">(v2)</span>
				</h4>
				<nav aria-label="breadcrumb">
					<ol class="breadcrumb">
						<li class="breadcrumb-item">
							<a href="#{pageName}">{pageName}</a>
						</li>
					</ol>
				</nav>
			</div>
			<UserProfile {...user} />
		</section>
	</div>
</header>

<style>
	.header {
		background-color: var(--black);
		padding: 15px 20px;
		position: relative;
		overflow: hidden;
		border-bottom: 1px solid var(--accent-blue);
		color: var(--white);
	}
	.breadcrumb {
		background-color: transparent;
		margin-bottom: 0;
		padding: 0;
	}

	.breadcrumb-item,
	.breadcrumb-item a {
		color: var(--white);
	}

	#navToggle:focus {
		border: 2.5px solid var(--cool-grey);
	}
</style>
