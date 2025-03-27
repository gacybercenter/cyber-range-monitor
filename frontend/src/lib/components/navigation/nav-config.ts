import type { NavButtonProps } from './navigation.types';

const navOption = (title: string, href: string, icon: string): NavButtonProps => {
	return { title, href, icon } as NavButtonProps;
};

const navDropdown = (
	title: string,
	href: string,
	icon: string,
	subOptions: NavButtonProps[]
): NavButtonProps => {
	return { title, href, icon, subOptions } as NavButtonProps;
};

const homeOption = (href: string) => navOption('home', href, 'fa-solid fa-house');

const openstackOptions = [
	homeOption('/openstack'),
	navOption('volumes', '/openstack/volumes', 'fa-solid fa-box'),
	navOption('networks', '/openstack/networks', 'fa-solid fa-wifi')
];

const saltstackOptions = [
	homeOption('/saltstack'),
	navOption('jobs', '/saltstack/jobs', 'fa-solid fa-plug-circle-check'),
	navOption('grains', '/saltstack/grains', 'fa-solid fa-wheat-awn'),
	navOption('states', '/saltstack/states', 'fa-solid fa-cogs')
];

const guacOptions = [
	homeOption('/guacamole'),
	navOption('connections', '/guacamole/connections', 'fa-solid fa-plug'),
	navOption('topology', '/guacamole/topology', 'fa-solid fa-diagram-project')
];

const NAVIGATION = [
	homeOption('/'),
	navOption('users', '/users', 'fa-regular fa-circle-user'),
	navOption('datasources', '/datasources', 'fa-solid fa-database'),
	navDropdown('openstack', '/openstack', 'fa-solid fa-cloud-arrow-down', openstackOptions),
	navDropdown('guacamole', '/guacamole', 'fa-solid fa-clapperboard', guacOptions),
	navDropdown('saltstack', '/saltstack', 'fa-solid fa-computer', saltstackOptions)
];

export default NAVIGATION;
