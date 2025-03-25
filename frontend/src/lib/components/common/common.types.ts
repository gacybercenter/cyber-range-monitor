export interface StatCardProps {
	title: string;
	value: string;
	badgeIcon: string;
	description: string;
}

export type CardItem = {
	title: string;
	subText?: string;
	icon: string;
};

export type AlertProps = {
	title: string;
	summary: string;
	type: 'success' | 'warning' | 'danger';
};
