import { getContext, onDestroy, setContext } from 'svelte';
import type { ToastOptions, ToastState } from './toast.types';

/**
 * Allows for the creation of toasts without prop drilling and
 * manages the timeouts to avoid memory leaks.
 */
class ToasterState {
	toasts = $state<ToastState[]>([]);
	timeouts = new Map<string, number>();

	constructor() {
		onDestroy(() => {
			for (const timeoutIds of this.timeouts.values()) {
				if (timeoutIds) {
					clearTimeout(timeoutIds);
				}
			}
			this.timeouts.clear();
			this.toasts.length = 0;
		});
	}

	create(title: string, message: string, options?: ToastOptions, ms: number = 5000) {
		const id = crypto.randomUUID();

		this.toasts.push({
			props: { title, message, options },
			id
		});

		this.timeouts.set(
			id,
			setTimeout(() => this.remove(id), ms)
		);
	}

	remove(id: string) {
		const timeout = this.timeouts.get(id);
		if (timeout) {
			clearTimeout(timeout);
			this.timeouts.delete(id);
		}
		this.toasts = this.toasts.filter((toast) => toast.id !== id);
	}
}

const TOASTER_ID = Symbol('Toaster');

/**
 * Initializes the toaster context.
 */
export const setToasterState = () => {
	setContext(TOASTER_ID, new ToasterState());
};

/**
 * Returns the state of the toaster
 */
export const getToasterState = () => {
	return getContext<ToasterState>(TOASTER_ID) as ToasterState;
};
