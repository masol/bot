{% set meta = {
    'fname': 'src/lib/components/header.svelte',
} %}


<script>
	import { Navbar, NavBrand, NavLi, NavUl, NavHamburger } from 'flowbite-svelte';
	import logo from '$lib/images/logo.png';
</script>

<Navbar
	navClass="px-2 sm:px-4 py-2.5 w-full sticky top-0 z-50 border-b-2 border-r-neutral-400"
	let:hidden
	let:toggle
>
	<NavBrand href="/{{subdir}}">
		<img src="{{img_300_300__logo_png}}" class="mr-3 h-6 sm:h-9" alt="Logo" />
		<!-- <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">品研网</span> -->
	</NavBrand>
	<div class="flex md:order-2">
		<NavHamburger on:click={toggle} class1="w-full md:flex md:w-auto md:order-1" />
	</div>
	<NavUl {hidden}>
		<NavLi href="/{{subdir}}" active={true}>home</NavLi>
		<NavLi href="/{{subdir}}">我的</NavLi>
	</NavUl>
</Navbar>
