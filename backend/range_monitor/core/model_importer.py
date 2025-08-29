from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SqlObjectImporter:
    root_package: str
    module_names: list[str]
    auto_error: bool = False

    def _walk(self, auto_error: bool = True):
        package = importlib.import_module(self.root_package)
        if not hasattr(package, '__path__'):
            return

        for _, modname, ispkg in pkgutil.walk_packages(package.__path__):
            if ispkg or modname not in self.module_names:
                continue
            try:
                importlib.import_module(modname)
                yield modname
            except Exception as e:
                if auto_error:
                    raise e
                logger.warning(f'Failed to import {modname}: {e}')

    def load_models(self) -> list[str]:
        modules = []
        for modname in self._walk(auto_error=self.auto_error):
            logger.info(f'Imported module: {modname}')
            modules.append(modname)

        if not modules:
            logger.warning(
                'No modules were imported; ensure the module structure is correct.'
            )

        return modules
