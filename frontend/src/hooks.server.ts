import Authorization from '$lib/server/auth';
import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	if (event.url.pathname.startsWith('/login')) {
		return await resolve(event);
	}
	const [data, error] = await Authorization.loadUserAuthorization(event);

	if (error || !data) {
		event.locals.user = null;
		event.locals.apiKey = null;
		throw redirect(
			307, 
			Authorization.loginRedirect(
				event, error || 'You are not authorized.'
			)
		);
	}

	const { user, apiKey } = data;

	event.locals.user = user;
	event.locals.apiKey = apiKey;

	event.cookies.set('apiKey', apiKey, Authorization.apiKeyCookie());

	return await resolve(event);
};
