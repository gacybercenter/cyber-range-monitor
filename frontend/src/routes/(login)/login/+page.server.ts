import type { Actions } from './$types';
import type { AuthForm } from '$lib/server/api/client';

import { AuthService } from '$lib/server/api/client';
import { fail, redirect } from '@sveltejs/kit';

export const actions: Actions = {
	defaukt: async ({ request }) => {
		const data = await request.formData();
		const [username, password] = [data.get('username'), data.get('password')];
		if (!username || !password) {
			return fail(400, {
				success: false,
				message: 'You must provide both a username and password'
			});
		}

		const response = await AuthService.login({
			body: { username, password } as AuthForm
		});

		if (response.status !== 200) {
			return fail(401, { success: false, message: 'Invalid username or password' });
		}

		throw redirect(303, '/');
	}
} satisfies Actions;
