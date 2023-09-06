// import adapter from '@sveltejs/adapter-auto';
import adapter from '@sveltejs/adapter-static'
import preprocess from "svelte-preprocess";


/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: [
		preprocess({
			postcss: true,
			 /** Add a custom language preprocessor */
		})
	],
	kit: {
		adapter: adapter({
		}),
		paths: {
      assets: '',
      base: ''
    }
	},
	vitePlugin: {
    experimental: {
      useVitePreprocess: true
    }
  }
};

export default config;
