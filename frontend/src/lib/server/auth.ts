import { type RequestEvent } from '@sveltejs/kit';
import { AuthService, UserService, type LoginUserResponse } from '../api/client';
import type { APIAuthorization, AuthData, FormResponse } from './server.types';

export const COOKIE_NAME = 'apiKey';

export const loginRedirect = (event: RequestEvent, message: string): string => {
	const redirectTo = event.url.pathname + event.url.search;
	return `/login?redirectTo=${redirectTo}&message=${message}`;
};

/**
 * logins a user and returns the success of the operation
 * which if fails has an error message and if success has the user
 * data.
 * @param username
 * @param password
 * @returns
 */
export const loginUser = async (
	username: string,
	password: string
): Promise<FormResponse<LoginUserResponse>> => {
	const loginResponse = await AuthService.loginUser({ body: { username, password } });
	const DEFAULT_ERR = 'Could not sign in.';

	if (loginResponse.error) {
		return { success: false, message: loginResponse.error.message || DEFAULT_ERR };
	}

	if (!loginResponse.data) {
		return { success: false, message: DEFAULT_ERR };
	}

	return {
		success: true,
		data: loginResponse.data as LoginUserResponse
	};
};

/**
 * Returns the required authorization the API requires
 * and the APIKey
 * @param event
 * @returns {APIAuthorization | null}
 */
export const getApiAuthorization = (event: RequestEvent): APIAuthorization | null => {
	const apiKey = event.cookies.get('apiKey');
	if (!apiKey) {
		return null;
	}
	return {
		headers: {
			Authorization: `Bearer ${apiKey}`
		},
		apiKey
	};
};

export const apiKeyCookieConfig = () => {
	const hourFromNow = 60 * 60 * 60;
	return {
		path: '/',
		httpOnly: true,
		sameSite: 'strict' as const,
		expires: new Date(Date.now() + hourFromNow * 1000), // 1 hour from now
		maxAge: hourFromNow // 1 hour in seconds
	};
};

type AuthLoader = [AuthData, null] | [null, string];

export const loadUserAuthorization = async (event: RequestEvent): Promise<AuthLoader> => {
	const apiAuth = getApiAuthorization(event);
	if (!apiAuth) {
		return [null, 'Not authorized.'];
	}

	const { apiKey, headers } = apiAuth;

	const userResponse = await UserService.getCurrentUser({ headers });
	if (userResponse.error || userResponse.status !== 200) {
		return [null, 'Session is invalid or has expired.'];
	}
	console.log('here');
	const authData = { apiKey, user: userResponse.data };
	return [authData, null] as AuthLoader;
};
