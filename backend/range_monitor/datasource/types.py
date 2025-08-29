from enum import StrEnum


class DataSourceType(StrEnum):
    GUACAMOLE = 'guacamole'
    OPENSTACK = 'openstack'
    SALTSTACK = 'saltstack'