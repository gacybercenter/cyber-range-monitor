import { defineConfig, defaultPlugins } from '@hey-api/openapi-ts';

export default defineConfig({
	input: './openapi.json',
	output: {
		path: './src/lib/api/client',
		lint: 'eslint',
		format: 'prettier'
	},
	plugins: [
		...defaultPlugins,
		'@hey-api/client-fetch',
		{
			asClass: true,
			operationId: true,
			name: '@hey-api/sdk'
		}
	]
});
