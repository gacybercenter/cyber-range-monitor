import { type Cookies, type RequestEvent } from '@sveltejs/kit';
import { type TokenClaim } from './api/client';
import { env } from '$env/dynamic/private';

const REFRESH_TOKEN_COOKIE_NAME = env.REFRESH_TOKEN_COOKIE_NAME || 'refresh_token';
const ACCESS_TOKEN_COOKIE_NAME = env.ACCESS_TOKEN_COOKIE_NAME || 'access_token';
const API_URL = env.API_URL || 'http://localhost:8000';
const REFRESH_TTL = parseInt(env.REFRESH_TOKEN_HOURS) * 60 * 60;
const ACCESS_TTL = parseInt(env.ACCESS_TOKEN_MINUTES) * 60;

export const redirectedLoginPath = (event: RequestEvent, message: string) => {
	const params = new URLSearchParams({
		redirectTo: event.url.pathname + event.url.search,
		message: message
	});
	return `/login?${params.toString()}`;
};

interface TokenCookies {
	accessToken?: string;
	refreshToken?: string;
}



export const setTokenCookies = (cookies: Cookies, claims: TokenClaim) => {

	const refreshMs = Date.now() + REFRESH_TTL * 1000;
	const expires= new Date(refreshMs);
	const baseCookieOptions = {
		httpOnly: true,
		sameSite: 'strict' as const,
		path: env.COOKIE_PATH || '/',
		expires
	};

	cookies.set(ACCESS_TOKEN_COOKIE_NAME, claims.accessToken, {
		...baseCookieOptions,
		maxAge: ACCESS_TTL
	});

	cookies.set(REFRESH_TOKEN_COOKIE_NAME, claims.refreshToken, {
		...baseCookieOptions,
		maxAge: REFRESH_TTL,
	});
};

export const clearTokenCookies = (cookies: Cookies) => {
	cookies.delete(ACCESS_TOKEN_COOKIE_NAME, { path: env.COOKIE_PATH || '/' });
	cookies.delete(REFRESH_TOKEN_COOKIE_NAME, { path: env.COOKIE_PATH || '/' });
};

export const getTokenCookies = (cookies: Cookies): TokenCookies => {
	const accessToken = cookies.get(ACCESS_TOKEN_COOKIE_NAME);
	const refreshToken = cookies.get(REFRESH_TOKEN_COOKIE_NAME);
	return { accessToken, refreshToken };
};

export const prepareApiFetch = async (
	event: RequestEvent,
	context: { request: Request, fetch: typeof fetch}
) => {
	const { request, fetch } = context;
	if(!request.url.startsWith(API_URL)) {
		return fetch(request);
	}

	const url = new URL(request.url);

	const isRefresh = url.pathname === '/auth/refresh';


	const { accessToken, refreshToken } = getTokenCookies(event.cookies);

	let headers = new Headers(event.request.headers);
	headers.set('Authorization', `Bearer ${accessToken}`);


	const response = await fetch(new Request(event.request.url, { headers }));
	if (response.status !== 401 || isRefresh) {
		return response;
	}

	const refreshResponse = await fetch(
		new Request(`${API_URL}/auth/refresh`, {
			method: 'POST',
			body: JSON.stringify({
				accessToken,
				refreshToken,
			}),
			headers: {
				'Content-Type': 'application/json',
				Accept: 'application/json'
			}
		})
	);
	if (!refreshResponse.ok) {
		return response;
	}
	const tokens = (await refreshResponse.json()) as TokenClaim;
	setTokenCookies(event.cookies, tokens);

	headers = new Headers(request.headers);
	headers.set('Authorization', `Bearer ${tokens.accessToken}`);

	return await fetch(new Request(event.request.url, { headers }));
};
