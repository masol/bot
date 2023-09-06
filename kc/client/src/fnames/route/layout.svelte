{% set meta = {
    'fname': 'src/routes/+layout.svelte',
} %}

<script>
	// @ts-ignore
	import Config from 'virtual:config';
	{% if subdir|length == 0 %}
	import Header from '$lib/components/header.svelte';
	import Footer from '$lib/components/footer.svelte';
	{% endif %}	
	let isDev = !!Config.dev;
	// let isDev = false // 如果在开发环境下使用编译模式，注释上一行，打开本行即可。
</script>

{% if subdir|length == 0 %}
<Header />
<hr />
<section class="bg-white dark:bg-gray-600 min84">
	<slot />
</section>
<Footer />
{% else %}
<slot />
{% endif %}

<svelte:head>
	{#if isDev}
		<script
			src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp"></script>
		<script>
			// 只在开发环境有效，调整配置与项目的tailwind.loadConfigFromFile.cjs相同。
			// tailwind.config = {
			//   theme: {
			//     extend: {
			//       colors: {
			//         clifford: '#da373d',
			//       }
			//     }
			//   }
			// }
		</script>
		<!-- <link crossorigin="anonymous" href="//lib.baomitu.com/tailwindcss/latest/tailwind.min.css" rel="stylesheet"> -->
	{/if}
</svelte:head>

<style global lang="postcss">
	@tailwind base;
	@tailwind components;
	@tailwind utilities;
	@tailwind variants;
	@tailwind screens;
	{% if subdir|length == 0 %}
	.min84 {
		min-height: 84vh;
	}
	{% endif %}
</style>

