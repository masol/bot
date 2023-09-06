import { sveltekit } from '@sveltejs/kit/vite';
import Config from './src/vite/config'

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [sveltekit(),Config()]
};

export default config;
