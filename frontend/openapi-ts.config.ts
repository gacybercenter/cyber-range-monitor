import { defineConfig, defaultPlugins } from '@hey-api/openapi-ts';

export default defineConfig({
	input: './openapi.json',
	output: {
		path: './src/lib/server/api/client',
		lint: 'eslint',
		format: 'prettier'
	},
	plugins: [
		...defaultPlugins,
		'zod',
		{
			name: '@hey-api/client-axios',
			runtimeConfigPath: './src/lib/server/hey-api.ts'
		},
		{
			asClass: true,
			operationId: true,
			name: '@hey-api/sdk',
			validator: true
		}
	]
});
