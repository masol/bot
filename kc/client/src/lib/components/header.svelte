<script>
	import { Button, Navbar, NavBrand, NavLi, NavUl, NavHamburger,Spinner,Popover,
		Dropdown,DropdownItem,DropdownHeader,DropdownDivider,Avatar} from 'flowbite-svelte';
	import logo from '$lib/images/logo.png';
	// import DarkMode from './darkmode.svelte';	
	//用两种不同的接口方式(rest/gql)来分别演示登录与注销的session管理．两者在服务器端是无状态的．
	import VarCtrl from '$lib/utils/vars/gqlvar';
	import RestvarCtrl from '$lib/utils/vars/restvar';	
	import { onMount } from 'svelte';
	import Device from 'svelte-device-info';
	import { page } from '$app/stores';	

	let canHover = false;
	onMount(async () => {
		console.log('document.cookie=', document.cookie);
		canHover = Device.canHover;
	});

	const meQpl = `{
  me{
    id,
    role,
	name,
	avatar,
	expires,
	group
  }
}`;

	const userVarCtrl = new VarCtrl({
		syncTpl: meQpl
	});
	const userInfo = userVarCtrl.var;

	// @see https://github.com/sveltejs/svelte/issues/3410
	let field;
	function handleRetry() {
		if (field) {
			field.$destroy();
		}
		userVarCtrl.query();
	}

	const logoutVarCtrl = new RestvarCtrl({
		syncTpl: '/v1/auth/logout',
		bWritable: true,
		varPath: {},
		initData: {},
		onErr: (data, that) => {
			if (String(data).indexOf('Error: Unauthorized') >= 0) {
				userVarCtrl.updData({ id: null }, 'me');
			}
			console.log('onErr!!', JSON.stringify(data));
		},
		onVal: (data, that) => {
			console.log('onVal');
			console.log('onVal 注销成功数据为:', data);
			userVarCtrl.updData({ id: null }, 'me');
		}
	})

	const handleLougout = logoutVarCtrl.getSubmit();


	$: activeUrl = $page.url.pathname;

</script>

<Navbar
	let:hidden
	let:toggle
>
	<NavBrand href="/{{subdir}}">
		<img src="{{img_300_300__logo_png}}" class="mr-3 h-6 sm:h-9" alt="Logo" />
		<!-- <span class="self-center whitespace-nowrap text-xl font-semibold dark:text-white">品研网</span> -->
	</NavBrand>
	<div class="flex md:order-2">
		{#if $userInfo.isResolved() && $userInfo.getData('me.id')}
		<Avatar id="user-drop" src="{$userInfo.data.me.avatar}" class="cursor-pointer" dot={ { color: 'green' } } />
		<Dropdown triggeredBy="#user-drop">
			<DropdownHeader>
			  <span class="block text-sm">{$userInfo.data.me.name}</span>
			  <span class="block truncate text-sm font-medium">{$userInfo.data.me.role}</span>
			</DropdownHeader>
			<DropdownItem>Dashboard</DropdownItem>
			<DropdownItem>Settings</DropdownItem>
			<DropdownItem>Earnings</DropdownItem>
			<DropdownDivider />
			<DropdownItem on:click={handleLougout}>注销</DropdownItem>
		  </Dropdown>
		{/if}
		<NavHamburger on:click={toggle} class1="w-full md:flex md:w-auto md:order-1" />
	</div>
	<NavUl {activeUrl} {hidden}>
		{#if $userInfo.isPending()}
			<NavLi><Spinner size={4} /></NavLi>
		{:else if $userInfo.isResolved() && $userInfo.getMeta('', 'errmsg')}
  		    <NavLi>
			  <Button
				on:click={handleRetry}
				id="refresh"
				btnClass="ripple-bg-gray-300 mr-3 px-4 py-2 bg-red-300 hover:bg-indigo-600 text-gray-50 rounded-xl flex items-center gap-2">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-5 w-5"
					viewBox="0 0 20 20"
					fill="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99"
					/>
				</svg>
				<span>刷新</span>
			</Button>
			{#if canHover}
				<Popover
					bind:this={field}
					placement="bottom"
					class="w-64 text-sm font-red "
					title="获取用户信息失败"
					triggeredBy="#refresh">{$userInfo.getMeta('', 'errmsg')}
				</Popover>
			{/if}
			</NavLi>
		{:else if $userInfo.isResolved() && $userInfo.getData('me.id')}
			<NavLi href="/{{subdir}}" active={true}>home</NavLi>
			<NavLi href="/{{subdir}}">我的</NavLi>
		{:else if $userInfo.isResolved() && !$userInfo.data.me.id}		
			<NavLi href="/auth/signin#suc={$page.url.pathname}" active={true}>登录</NavLi>
		{/if}
	</NavUl>
</Navbar>
