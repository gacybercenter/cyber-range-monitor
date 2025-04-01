import type { Actions } from './$types';

import { loginUser, apiKeyCookieConfig } from '$lib/server/auth';
import { fail, redirect } from '@sveltejs/kit';

export const actions: Actions = {
	default: async ({ request, cookies, url }) => {
		const data = await request.formData();
		const [username, password] = [data.get('username'), data.get('password')];
		if (!username || !password) {
			return fail(400, {
				success: false,
				message: 'You must provide both a username and password to sign in.'
			});
		}

		const authResult = await loginUser(username.toString(), password.toString());

		if (!authResult.success) {
			return fail(401, {
				success: false,
				message: authResult.message || 'Invalid username or password.'
			});
		}

		const { apiKey } = authResult.data;

		cookies.set('apiKey', apiKey, apiKeyCookieConfig());

		const redirectTo = url.searchParams.get('redirectTo') || '/';
		redirect(303, redirectTo);
	}
} satisfies Actions;
