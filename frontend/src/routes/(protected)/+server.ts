import type { RequestHandler } from '@sveltejs/kit';
import { AuthService } from '$lib/server/api/client';
import { redirect } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals }) => {
	await AuthService.logout({ throwOnError: false });
	locals.user = undefined;
	throw redirect(303, '/login');
};
