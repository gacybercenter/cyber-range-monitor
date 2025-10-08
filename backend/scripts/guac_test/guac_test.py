import base64
import dataclasses as dc
import os
import pprint
import time
from pathlib import Path
from typing import Iterable, Self, TypedDict

import guacamole
from pydantic import BaseModel, ConfigDict, Field


def to_camel_case(string: str) -> str:
    """
    Pydantic alias generator to convert snake_case to camelCase
    when `model_dump()` is called which automatically makes snake
    case to camel case conversions for keys in dicts.
    """
    words = string.split('_')
    new_name = []
    for i, word in enumerate(words):
        if i:
            new_name.append(word.capitalize())
        else:
            new_name.append(word.lower())

    return ''.join(new_name).replace('Id', 'Id')


def kebab_to_snake(string: str) -> str:
    return string.replace('-', '_')


class GuacamoleDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
    )

    def pprint(self) -> None:
        pprint.pprint(self.model_dump())


def get_session() -> guacamole.session:






def on_startup():
    os.chdir(Path(__file__).parent)











def extract_connections(obj: object) :
    conns = []
    active_conn_sum = 0

    stack = [obj]

    while stack:
        current = stack.pop()

        if isinstance(current, dict):
            if current.get('name') and current.get('identifier'):
                conn = current.copy()
                conn['activeConnections'] = int(conn['activeConnections'])

                if groups := conn.pop('childConnectionGroups', None):
                    stack.append(groups)

                if child_conn := conn.pop('childConnections', None):
                    stack.append(child_conn)

                conns.append({
                    'active_connections': conn.get('activeConnections', 0),
                    'identifier': conn.get('identifier', ''),
                    'name': conn.get('name', ''),
                    'parent_identifier': conn.get('parentIdentifier'),
                    'connection_type': conn.get('type'),
                })
                active_conn_sum += conn.get('activeConnections', 0)

            else:
                for value in current.values():
                    if isinstance(value, (dict, list)):
                        stack.append(value)

        elif isinstance(current, list):
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append(item)

    return conns, active_conn_sum




def detail_demo(sess: guacamole.session) -> None:

    data = sess.detail_connection(
        '14278',
        'parameters'
    )
    pprint.pprint(data)

    options = {
        'parameters': {},
        'history': {},
        'sharing profiles': {}
    }

    for key, value in options.items():
        print(f'--- {key} ---')
        data = sess.detail_connection(
            '14278',
            key
        )
        pprint.pprint(data)
        input()


class OutputDetail(TypedDict):
    func_called: str
    label: str
    output: dict

def add_md_output(detail: OutputDetail, md_lines: list[str]) -> None:
    pretty_json = pprint.pformat(detail['output'], indent=2)
    md_lines.extend([
        f"## `{detail['func_called']}` - {detail['label']}",
        '<summary>\nOutput JSON\n<details>\n',
        f'```json\n{pretty_json}\n```\n',
        '</details>\n</summary>\n',
    ])




def main() -> None:

    os.makedirs('output', exist_ok=True)

    sess = Startup.get_guacamole_session()

    topology = sess.list_connection_group_connections()

    output =



if __name__ == '__main__':
    main()
