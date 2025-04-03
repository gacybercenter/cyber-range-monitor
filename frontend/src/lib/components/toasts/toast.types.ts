export type ToastOptions = {
	icon?: string;
	iconColor?: string;
	preset?: 'primary' | 'secondary' | 'success' | 'danger';
};

export type ToastProps = {
	title: string;
	message: string;
	options?: ToastOptions;
};

export type ToastState = {
	props: ToastProps;
	id: string;
};
