import type { Actions } from './$types';
import {
	apiKeyCookieConfig,
	COOKIE_NAME,
	getApiAuthorization,
	loginRedirect
} from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';
import { AuthService } from '$lib/api/client';

export const actions: Actions = {
	logout: async (event) => {
		const auth = getApiAuthorization(event);

		if (!auth) {
			throw redirect(307, loginRedirect(event, 'Cannot signout when unauthorized'));
		}

		const { headers } = auth;

		await AuthService.logoutUser({ headers });

		event.cookies.delete(COOKIE_NAME, apiKeyCookieConfig());

		throw redirect(307, '/login');
	}
};
