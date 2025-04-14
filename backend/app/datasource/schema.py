from enum import StrEnum


class Datasources(StrEnum):
    guacamole = 'guacamole'
    openstack = 'openstack'
    saltstack = 'saltstack'