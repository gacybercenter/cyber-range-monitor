# app/startup.py
from __future__ import annotations

import functools
import importlib
import logging
import pkgutil
from dataclasses import dataclass

from sqlalchemy.orm import configure_mappers

logger = logging.getLogger(__name__)

@dataclass
class ImportIterator:
    root_package: str
    module_basename: str

    def walk(self, auto_error: bool = True):
        package = importlib.import_module(self.root_package)
        if not hasattr(package, '__path__'):
            return

        prefix = package.__name__ + '.'
        for _, modname, ispkg in pkgutil.walk_packages(package.__path__, prefix):
            mod_basename = modname.rsplit('.', 1)[-1]
            if not ispkg and mod_basename == self.module_basename:
                try:
                    importlib.import_module(modname)
                    yield modname
                except Exception as e:
                    if auto_error:
                        raise e
                    logger.warning(f"Failed to import {modname}: {e}")

@functools.lru_cache
def load_mapped_models(
    *,
    root_package: str = 'app',
    module_basename: str = 'model',
    auto_error: bool = False
) -> list[str]:
    """
    Imports all `domain` models by checking the module for the basename specified
    this allows for us to map our models to sqlalchemy without having to follow
    a strict directory structure.

    Example
    -------
    root_package='app.domains', module_basename='model'
    Imports every module in `app.domains.[pkg].model` .

    Returns
    -------
    list[str]
        _description_
    """

    domain_iterator = ImportIterator(
        root_package=root_package,
        module_basename=module_basename
    )

    imported_models: list[str] = []
    for modname in domain_iterator.walk(auto_error=auto_error):
        imported_models.append(modname)

    if not imported_models:
        logger.warning(
            'No domain models were imported, ensure that the domain model '
            'modules are correctly defined and contain the expected model classes.'
        )
    return imported_models
