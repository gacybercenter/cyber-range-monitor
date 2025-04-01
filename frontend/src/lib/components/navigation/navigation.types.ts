export interface NavOptionProps {
	title: string;
	icon: string;
	href: string;
}

export interface NavButtonProps extends NavOptionProps {
	subOptions?: NavOptionProps[];
}

export type NavigationProps = {
	open: boolean;
}
