// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { UserResponse } from '$lib/api/client';
declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user: UserResponse | null;
			apiKey: string | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
