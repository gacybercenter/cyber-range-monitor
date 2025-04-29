import type { UserResponse } from './api/client';

export type APIAuthorization = {
	headers: { Authorization: string };
	apiKey: string;
};

export type AuthData = {
	apiKey: string;
	user: UserResponse;
};

export type FormError = {
	success: false;
	message: string;
};

export type FormSuccess<T> = {
	success: true;
	data: T;
	message?: string;
};

export type FormResponse<T> = FormError | FormSuccess<T>;

export type AuthLoader = [AuthData, null] | [null, string];
