import { UserService } from '$lib/server/api/client';
import type { Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	if (event.url.pathname.startsWith('/login')) {
		return await resolve(event);
	}
	const response = await UserService.currentUser();
	event.locals.user = response.data;
	return await resolve(event);
};
