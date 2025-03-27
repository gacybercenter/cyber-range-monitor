<script lang="ts">
	import StatCard from '$lib/components/common/StatCard.svelte';
	import ContentBlock from '$lib/components/ContentBlock.svelte';

	let { data } = $props();
	

</script>

<ContentBlock>
	<StatCard
			title="test"
			badgeIcon="fa-solid fa-network-wired"
			value="100"
			description="This is a test description for the stat card."
			--badge-color="var(--accent-blue)"
		/>
		<StatCard
			title="test"
			badgeIcon="fa-solid fa-network-wired"
			value="100"
			description="This is a test description for the stat card."
			--badge-color="var(--accent-blue)"
		/>
		<StatCard
			title="test"
			badgeIcon="fa-solid fa-network-wired"
			value="100"
			description="This is a test description for the stat card."
			--badge-color="var(--accent-blue)"
		/>
		<StatCard
			title="test"
			badgeIcon="fa-solid fa-network-wired"
			value="100"
			description="This is a test description for the stat card."
			--badge-color="var(--accent-blue)"
		/>
</ContentBlock>
