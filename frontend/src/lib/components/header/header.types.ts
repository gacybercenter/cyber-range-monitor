export type UserProfileProps = {
	username: string;
	role: string;
	onLogout: () => Promise<void>;
};

export type AppHeaderProps = {
	pageName: string;
	starCount?: number;
	user: UserProfileProps;
	navToggleHandler: VoidFunction;
};

export type StarbackgroundProps = {
	starCount: number;
};
