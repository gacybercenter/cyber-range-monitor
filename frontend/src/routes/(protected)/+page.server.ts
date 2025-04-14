import type { Actions } from './$types';
import Authorization from '$lib/server/auth';
import { redirect } from '@sveltejs/kit';
import { AuthService } from '$lib/api/client';

export const actions: Actions = {
	logout: async (event) => {
		const auth = Authorization.getKeyBearer(event);

		if (!auth) {
			throw redirect(307, Authorization.loginRedirect(event, 'Cannot signout when unauthorized'));
		}

		const { headers } = auth;

		await AuthService.logoutUser({ headers });

		event.cookies.delete(Authorization.COOKIE_NAME, Authorization.apiKeyCookie());

		throw redirect(307, '/login');
	}
};
