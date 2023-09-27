<script>
	// @ts-nocheck

	import { Helper, Input, Label, Checkbox, P } from 'flowbite-svelte';

	import VarCtrl from '$lib/utils/vars/restvar';
	import SignupSchema from '$lib/schemas/signup.json';
	import HasherCtrl from '$lib/utils/vars/hashvar';

	import signup from '$lib/images/signup.jpg';

	const hashctrl = HasherCtrl.inst

	const signupVarCtrl = new VarCtrl({
		syncTpl: '/v1/auth/reg',
		bWritable: true,
		varPath: 'me',
		initData: {
			me: {
				username: '',
				password: '',
				confirmpwd: ''
			}
		},
		validator: {
			path: 'me',
			schema: SignupSchema
		},
		onErr: (data, that) => {
			//手动更新友好的错误提示．无需返回true继续更新．
			// console.log("data=",String(data))
			// if (String(data).indexOf('Error: Unauthorized') >= 0) {
			// 	//未登录错误，视同成功．
			// 	procLogout();
			// } else {
			that.updMeta(
				{
					bValid: false,
					errmsg: '注册失败!'
				},
				'me'
			);
			// }
		},
		onVal: (data, that) => {
			console.log('注册成功数据为:', data);
			// console.log("getData=",HasherCtrl.inst.$var.getData('suc','/'))
			window.location.href = HasherCtrl.inst.$var.getData('suc', '/');
			// that.updMeta(
			// 	{
			// 		bValid: true,
			// 		errmsg: ''
			// 	},
			// 	'me'
			// );
			// return true //继续将data更新回tgtPath上．
		}
	});
	const signupVar = signupVarCtrl.var;
	const usernameSetter = signupVarCtrl.getEvtTrans('me.username');
	// console.log("loginVar=",loginVar)

	const handleSubmit = signupVarCtrl.getSubmit();
</script>

<div class="bg-white dark:bg-gray-900">
	<div class="flex justify-center h-screen">
		<div
			class="hidden bg-cover lg:block lg:w-2/3"
			style="background-image: url({{img_800_800__signup_jpg}})"
		>
			<div class="flex items-center h-full px-20 bg-gray-900 bg-opacity-40">
				<div>
					<h2 class="text-4xl font-bold text-white">Brand</h2>

					<p class="max-w-xl mt-3 text-gray-300">
						Lorem ipsum dolor sit, amet consectetur adipisicing elit. In autem ipsa, nulla
						laboriosam dolores, repellendus perferendis libero suscipit nam temporibus molestiae
					</p>
				</div>
			</div>
		</div>

		<div class="flex items-center w-full max-w-md px-6 mx-auto lg:w-2/6">
			<div class="flex-1">
				<div class="text-center">
					<h2 class="text-4xl font-bold text-center text-gray-700 dark:text-white">品研网</h2>

					<p class="mt-3 text-gray-500 dark:text-gray-300">使用您的品研帐号登录</p>
				</div>

				<div class="mt-8">
					<form on:submit={handleSubmit}>
						<Helper helperClass="mb-3" color={$signupVar.mValid('me')}>
							{#if $signupVar.getMeta('me', 'errmsg')}
								{$signupVar.getMeta('me', 'errmsg')}
							{:else if $signupVar.getMeta('me', 'bValid', false)}
								{#if $signupVar.isPending()}
									<span class="font-medium">登录中,请稍候</span> submit: Some prompt messsage.
								{:else}
									<span class="font-medium">Well done!</span> submit: Some success messsage.
								{/if}
							{:else}
								<span class="font-medium">初始提示:</span> submit: Some messsage.
							{/if}
						</Helper>
						<div>
							<Label for="username" color="gray" class="block mb-2">您的标识</Label>
							<Input
								on:blur={usernameSetter}
								name="username"
								color={$signupVar.mValid('me.username')}
								id="username"
								placeholder="用户名|手机号|邮箱|身份证号"
							>
								<svg
									slot="left"
									viewBox="0 0 24 24"
									stroke="currentColor"
									stroke-width="2"
									fill="none"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="h-4 w-4"
								>
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
									<circle cx="12" cy="7" r="4" />
								</svg>
							</Input>
							<Helper class="mt-2" color={$signupVar.mValid('me.username')}>
								{#if $signupVar.getMeta('me.username', 'errmsg')}
									{$signupVar.getMeta('me.username', 'errmsg')}
								{:else if $signupVar.getMeta('me.username', 'bValid', false)}
									<span class="font-medium">Well done!</span> Some success messsage.
								{:else}
									<span class="font-medium">初始提示:</span> Some messsage.
								{/if}
							</Helper>
						</div>

						<div class="mt-6">
							<Label for="password" color="gray" class="block mb-2"
								>您的密码 <a
									href="/"
									class="float-right text-sm text-gray-400 focus:text-blue-500 hover:text-blue-500 hover:underline"
									>忘记密码?</a
								></Label
							>

							<Input
								bind:value={$signupVar.data.me.password}
								name="password"
								color={$signupVar.mValid('me.password')}
								id="password"
								type="password"
								placeholder="******"
							>
								<svg
									slot="left"
									viewBox="0 0 64 64"
									stroke="currentColor"
									stroke-width="2"
									fill="none"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="h-5 w-5"
								>
									<path
										d="M34.3,34,53.17,17.55a4.09,4.09,0,0,0,.39-5.77h0a4.09,4.09,0,0,0-5.77-.4l-1.49,1.3,0,0L42.94,13l-.66,3.2a.05.05,0,0,1,0,.05l-1,.84-.06,0L38,17.24l-.55,3.11a.09.09,0,0,1,0,.06l-1.54,1.35-.06,0L32.57,22l-.51,3.06a.06.06,0,0,1,0,.06l-3.68,3.21-.4-.17a11.89,11.89,0,1,0,6.61,6.4Z"
										stroke-linecap="round"
									/><circle cx="20.71" cy="41.77" r="3.07" stroke-linecap="round" />
								</svg>
							</Input>
							<Helper class="mt-2" color={$signupVar.mValid('me.password')}
								><span class="font-medium">
									{#if $signupVar.getMeta('me.password', 'errmsg')}
										{$signupVar.getMeta('me.password', 'errmsg')}
									{:else if $signupVar.getMeta('me.password', 'bValid', false)}
										<span class="font-medium">Well done!</span> Some success messsage.
									{:else}
										<span class="font-medium">初始提示:</span> Some messsage.
									{/if}
								</span></Helper
							>
						</div>

						<div class="mt-6">
							<Label for="confirmpwd" color="gray" class="block mb-2"
								>重复密码</Label>

							<Input
								bind:value={$signupVar.data.me.confirmpwd}
								name="confirmpwd"
								color={$signupVar.mValid('me.confirmpwd')}
								id="confirmpwd"
								type="password"
								placeholder="******"
							>
								<svg
									slot="left"
									viewBox="0 0 64 64"
									stroke="currentColor"
									stroke-width="2"
									fill="none"
									stroke-linecap="round"
									stroke-linejoin="round"
									class="h-5 w-5"
								>
									<path
										d="M34.3,34,53.17,17.55a4.09,4.09,0,0,0,.39-5.77h0a4.09,4.09,0,0,0-5.77-.4l-1.49,1.3,0,0L42.94,13l-.66,3.2a.05.05,0,0,1,0,.05l-1,.84-.06,0L38,17.24l-.55,3.11a.09.09,0,0,1,0,.06l-1.54,1.35-.06,0L32.57,22l-.51,3.06a.06.06,0,0,1,0,.06l-3.68,3.21-.4-.17a11.89,11.89,0,1,0,6.61,6.4Z"
										stroke-linecap="round"
									/><circle cx="20.71" cy="41.77" r="3.07" stroke-linecap="round" />
								</svg>
							</Input>
							<Helper class="mt-2" color={$signupVar.mValid('me.confirmpwd')}
								><span class="font-medium">
									{#if $signupVar.getMeta('me.confirmpwd', 'errmsg')}
										{$signupVar.getMeta('me.confirmpwd', 'errmsg')}
									{:else if $signupVar.getMeta('me.confirmpwd', 'bValid', false)}
										<span class="font-medium">Well done!</span> Some success messsage.
									{:else}
										<span class="font-medium">初始提示:</span> Some messsage.
									{/if}
								</span></Helper
							>
						</div>


						<div class="mt-6">
							<button
								type="submit"
								class="w-full px-4 py-2 tracking-wide text-white transition-colors duration-200 transform bg-blue-500 rounded-md hover:bg-blue-400 focus:outline-none focus:bg-blue-400 focus:ring focus:ring-blue-300 focus:ring-opacity-50"
							>
								注册
							</button>
						</div>
					</form>

					<p class="mt-6 text-sm text-center text-gray-400">
						已有帐号， <a
							href="signin"
							class="text-blue-500 focus:outline-none focus:underline hover:underline">立即登录</a
						>。
					</p>
				</div>
			</div>
		</div>
	</div>
</div>
