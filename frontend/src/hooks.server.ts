import {
	loadUserAuthorization,
	apiKeyCookieConfig,
	COOKIE_NAME,
	loginRedirect
} from '$lib/server/auth';
import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	if (event.url.pathname === '/login') {
		return await resolve(event);
	}
	console.log('here');

	const [data, error] = await loadUserAuthorization(event);

	if (error || !data) {
		event.locals.user = null;
		event.locals.apiKey = null;
		throw redirect(307, loginRedirect(event, error || 'You are not authorized.'));
	}

	const { user, apiKey } = data;

	event.locals.user = user;
	event.locals.apiKey = apiKey;

	event.cookies.set('apiKey', apiKey, apiKeyCookieConfig());

	return await resolve(event);
};
