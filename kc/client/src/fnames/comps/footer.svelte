{% set meta = {
    'fname': 'src/lib/components/footer.svelte',
} %}

<script>
	import { SpeedDial, SpeedDialButton } from 'flowbite-svelte';
</script>

<footer
	class="p-4 bg-gray-200 rounded-lg shadow md:flex md:items-center md:justify-between md:p-6 dark:bg-gray-800"
>
	<span class="text-sm text-gray-500 sm:text-center dark:text-gray-400"
		>© 2015-{{current_year}} XXXX™(<a
			href="https://beian.miit.gov.cn/"
			class="hover:underline" target="_blank">京ICP备XXXXX号</a
		>) - XXXXXXX™(<a
			href="https://beian.miit.gov.cn/"
			class="hover:underline" target="_blank">京ICP备XXXX号</a
		>)
	</span>
	<ul class="pr-12 flex flex-wrap items-center mt-3 text-sm text-gray-500 dark:text-gray-400 sm:mt-0">
		<li>
			<a href="#" class="mr-4 hover:underline md:mr-6 ">About</a>
		</li>
		<li>
			<a href="#" class="mr-4 hover:underline md:mr-6">Privacy Policy</a>
		</li>
		<li>
			<a href="#" class="mr-4 hover:underline md:mr-6">Licensing</a>
		</li>
	</ul>
  <SpeedDial tooltip="none" textOutside>
    <SpeedDialButton name="分享" tooltip="none">
      <svg
        aria-hidden="true"
        class="w-6 h-6 "
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
        ><path
          d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"
        /></svg
      >
    </SpeedDialButton>
    <SpeedDialButton name="打印" tooltip="none">
      <svg
        aria-hidden="true"
        class="w-6 h-6"
        fill="currentColor"
        viewBox="0 0 20 20"
        xmlns="http://www.w3.org/2000/svg"
        ><path
          fill-rule="evenodd"
          d="M5 4v3H4a2 2 0 00-2 2v3a2 2 0 002 2h1v2a2 2 0 002 2h6a2 2 0 002-2v-2h1a2 2 0 002-2V9a2 2 0 00-2-2h-1V4a2 2 0 00-2-2H7a2 2 0 00-2 2zm8 0H7v3h6V4zm0 8H7v4h6v-4z"
          clip-rule="evenodd"
        /></svg
      >
    </SpeedDialButton>
    <SpeedDialButton name="页首" tooltip="none">
      <svg
        aria-hidden="true"
        class="w-6 h-6"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 32 32"
        fill="currentColor"
        preserveAspectRatio="xMidYMid meet"
      >
        <path d="M16 14L6 24 7.4 25.4 16 16.8 24.6 25.4 26 24zM4 8H28V10H4z" />
      </svg>
    </SpeedDialButton>
  </SpeedDial>
</footer>
