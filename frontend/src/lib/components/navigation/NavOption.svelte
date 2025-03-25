<script lang="ts">
	import type { NavOptionProps } from './navigation.types';

	let { title, href, icon }: NavOptionProps = $props();
</script>

<li class="nav-option-item" id="navOption-{title}">
	<a {href} class="option-anchor">
		<i class={icon}></i>
		{title}
	</a>
</li>
