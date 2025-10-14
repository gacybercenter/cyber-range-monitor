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
		{
			name: '@hey-api/client-fetch',
			runtimeConfigPath: './src/lib/server/hey-api.ts'
		},
		{
			operationId: true,
			name: '@hey-api/sdk',
		}
	]
});
