import type { LayoutServerLoad } from './$types';

export const load = (async ({ locals }) => {
	return {
		apiKey: locals.apiKey,
		user: locals.user
	};
}) satisfies LayoutServerLoad;
