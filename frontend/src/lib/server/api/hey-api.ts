import type { CreateClientConfig } from './client/client.gen';

export const createClientConfig: CreateClientConfig = (config) => ({
	...config,
	baseURL: 'http://127.0.0.1:8000',
	headers: {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	},
	throwOnError: false
});
