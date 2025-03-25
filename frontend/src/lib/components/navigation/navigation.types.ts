export interface NavOptionProps {
	title: string;
	icon: string;
	href: string;
}

export interface DropdownNavProps extends NavOptionProps {
	subOptions: NavOptionProps[];
}

export interface NavButtonProps extends NavOptionProps {
	subOptions?: NavOptionProps[];
}

export interface NavigationProps {
	menuOptions: NavButtonProps[];
	open: boolean;
	closeBtnClicked: VoidFunction;
}
