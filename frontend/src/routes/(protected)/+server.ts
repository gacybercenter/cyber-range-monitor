import type { RequestEvent, RequestHandler } from './$types';
import { apiKeyCookieConfig, getApiAuthorization, loginRedirect } from '$lib/server/auth';
import { AuthService } from '$lib/api/client';
import { redirect } from '@sveltejs/kit';

/**
 * Signs out the user and redirects to the login page
 * @param event {RequestEvent}
 */
export const POST: RequestHandler = async (event: RequestEvent) => {
	const auth = getApiAuthorization(event);
	if (!auth) {
		throw redirect(307, loginRedirect(event, 'Cannot signout when unauthorized'));
	}

	const { headers } = auth;
	await AuthService.logoutUser({ headers });
	event.cookies.delete('apiKey', apiKeyCookieConfig());
	throw redirect(307, '/login');
};
