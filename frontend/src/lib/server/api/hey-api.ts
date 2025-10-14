import type { CreateClientConfig } from './client/client.gen';
import { env } from '$env/dynamic/private';

/**
 * creates a client config for the hey-api client at run time
 * allowing for dynamic instead of static configuration for use
 * with environment variables
 */
export const createClientConfig: CreateClientConfig = (config) => ({
	...config,
	baseURL: 'http://127.0.0.1:8000',
	headers: {
		'Content-Type': 'application/json',
		Accept: 'application/json'
	}
});
