from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.core.pydantic import PydanticMixin
from range_monitor.datasource.repos import D, DatasourceRepo
from range_monitor.errors import ConflictError, EmptyPatchError, ResourceNotFound
from range_monitor.security import EncryptionPolicy

S = TypeVar('S', bound=PydanticMixin)

class DatasourceService(Generic[D, S]):
    response_model: type[S]
    repo_class: type[DatasourceRepo[D]]

    def __init__(self, encryption: EncryptionPolicy, db: AsyncSession) -> None:
        self.encryption: EncryptionPolicy = encryption
        self.repo = self.repo_class(db)

    async def read_by_id(self, datasource_id: str) -> S:

        if not (datasource := await self.repo.get_by_id(datasource_id)):
            raise ResourceNotFound(self.repo.read.table_name)

        return self.response_model.convert(datasource)

    async def toggle_datasource(self, datasource_id: str) -> S:

        if not (datasource := await self.repo.toggle_by_id(datasource_id)):
            raise ResourceNotFound(self.repo.read.table_name)

        return self.response_model.convert(datasource)

    async def delete_datasource(self, datasource_id: str) -> None:
        if not await self.repo.delete_by_id(datasource_id):
            raise ResourceNotFound(self.repo.read.table_name)


    def encrypt_password(self, password: str) -> str:
        cipher_bytes = self.encryption.fernet.encrypt(password.encode('utf-8'))
        return cipher_bytes.decode('utf-8')

    def decrypt_password(self, ciphertext: str) -> str:
        plain_bytes = self.encryption.fernet.decrypt(ciphertext.encode('utf-8'))
        return plain_bytes.decode('utf-8')

    async def patch_datasource(
        self,
        datasource_id: str,
        patch_body: PydanticMixin
    ) -> S:
        if not (params := patch_body.dump()):
            raise EmptyPatchError()

        if not (datasource := await self.repo.get_by_id(datasource_id)):
            raise ResourceNotFound(self.repo.read.table_name)

        if password := params.pop('password', None):
            params['password_cipher'] = self.encrypt_password(password)

        updated = await self.repo.patch(datasource, params)
        if not updated:
            raise ConflictError('label_already_exists')

        return self.response_model.convert(updated)

    async def get_credentials(self, datasource_id: str) -> tuple[str, D]:
        if not (datasource := await self.repo.get_by_id(datasource_id)):
            raise ResourceNotFound(self.repo.read.table_name)

        password = self.decrypt_password(datasource.password_cipher)
        return password, datasource