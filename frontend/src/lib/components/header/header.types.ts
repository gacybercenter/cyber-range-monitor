export type UserProfileProps = {
	username: string;
	role: string;
	onLogout: VoidFunction;
};

export type AppHeaderProps = {
	pageName: string;
	starCount?: number;
	user: UserProfileProps;
	menuOpenBtnClick: VoidFunction;
};

export type StarbackgroundProps = {
	starCount: number;
};
