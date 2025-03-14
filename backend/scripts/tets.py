from guacamole import session

from openstack import connection
import openstack

from pprint import pprint

from rich.traceback import install

install(show_locals=True)


def main() -> None:

    openstack.enable_logging(debug=True)
    conn = connection.Connection(
        region_name='RegionOne',
        auth={

        },
        identity_api_version='3'
    )

    pprint(conn.list_servers())


if __name__ == '__main__':
    main()
