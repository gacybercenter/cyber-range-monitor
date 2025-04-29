import { type RequestEvent } from '@sveltejs/kit';
import { AuthService, UserService, type LoginUserResponse } from './api/client';
import type { APIAuthorization, AuthLoader, FormResponse } from './server.types';

class Authorization {
	static COOKIE_NAME: string = 'apiKey';

	/**
	 * Returns the redirect URL to the login page with the redirectTo and
	 * an error message.
	 */
	static loginRedirect(event: RequestEvent, message: string): string {
		const redirectTo = event.url.pathname + event.url.search;
		return `/login?redirectTo=${redirectTo}&message=${message}`;
	}

	/**
	 * Resolves the apiKey cookie into the proper Authorization header to
	 * present to the API and then validates it by calling the API to refresh
	 * the user information to ensure the authorization is still valid.
	 */
	static async loadUserAuthorization(event: RequestEvent): Promise<AuthLoader> {
		const apiAuth = Authorization.getKeyBearer(event);
		if (!apiAuth) {
			return [null, 'Not authorized.'];
		}

		const { apiKey, headers } = apiAuth;

		const userResponse = await UserService.getCurrentUser({ headers });
		if (userResponse.error || userResponse.status !== 200) {
			return [null, 'Session is invalid or has expired.'];
		}
		const authData = { apiKey, user: userResponse.data };
		return [authData, null];
	}

	/**
	 * The parameters and configuration for the apiKey Cookie
	 */
	static apiKeyCookie() {
		const hourFromNow = 60 * 60 * 60;
		return {
			path: '/',
			httpOnly: true,
			sameSite: 'strict' as const,
			expires: new Date(Date.now() + hourFromNow * 1000), // 1 hour from now
			maxAge: hourFromNow // 1 hour in seconds
		};
	}

	/**
	 * Resolves the API Key into the Authorization header to be used by the API
	 */
	static getKeyBearer(event: RequestEvent): APIAuthorization | null {
		const apiKey = event.cookies.get(Authorization.COOKIE_NAME);
		if (!apiKey) {
			return null;
		}
		return {
			headers: {
				Authorization: `Bearer ${apiKey}`
			},
			apiKey
		};
	}

	/**
	 * Given the credentials of a user, sends them to the
	 * API to login and returns the response / success of the operation.
	 */
	static async loginUser(
		username: string,
		password: string
	): Promise<FormResponse<LoginUserResponse>> {
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
	}
}

export default Authorization;
