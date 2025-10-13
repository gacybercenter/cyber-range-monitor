import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.sources.base.controller import DatasourceController
from range_monitor.sources.base.errors import DatasourceToggleError
from range_monitor.sources.guacamole_source.model import GuacamoleSource
from range_monitor.sources.guacamole_source.schema import (
    GuacamoleCreate,
    GuacamoleRead,
    GuacamoleUpdate,
)

"""
since the base service / controller class is "abstract" and to save
you time from finding the methods that will raise NotImplementedError
by using the base class, list below are the ones safe to test for the
base class.

- get_by_id
- enable/disable/toggle
- get_enabled_source
- require_enabled
- create_datasource (kind of) - the private _validate_schema by default just serializes the schema passed so
    it's very limited to test)
- update_by_id
- delete_by_id
- read_datasource_password
"""


def source_args(
    username: str,
    password: str = 'pwd',
    endpoint: str = 'http://localhost:5000/v3',
    datasource: str = 'foo',
    enabled: bool = False,
) -> dict:
    return {
        'username': username,
        'password': password,
        'endpoint': endpoint,
        'datasource': datasource,
        'enabled': enabled,
    }


@pytest_asyncio.fixture(scope='module', autouse=True)
async def test_guac_seed(test_db: AsyncSession) -> None:
    test_seed = [
        source_args('guac_bar', enabled=True),
        source_args('guac_foo'),
        source_args('guac_baz'),
    ]
    test_db.add_all([GuacamoleSource(**seed) for seed in test_seed])
    await test_db.commit()


TestService = DatasourceController[
    GuacamoleSource, GuacamoleRead
]  # shortest java class definition


async def get_first_status(
    controller: TestService, enabled_flag: bool
) -> GuacamoleSource:
    """Get the first disabled or enabled datasource"""
    disabled = await controller.get_by(
        GuacamoleSource.enabled.is_(enabled_flag), controller.db
    )
    if not enabled_flag:
        err = (
            'The autouse fixture should ensure that more than one datasource exists '
            ' and is not working which will break several test cases.'
        )
    else:
        err = 'There were no enabled datasources found likely due to a test cases side effect.'
    assert disabled is not None, err
    return disabled


async def assert_total_enabled_eq(
    expected: int, controller: TestService
) -> list[GuacamoleSource]:
    """Assert that the total number of enabled models is as expected"""
    enabled_models = await controller.get_all(
        controller.db, GuacamoleSource.enabled.is_(True)
    )
    count = len(enabled_models) == expected
    assert count, (
        f'There should be {expected} enabled models in the database after this test.'
        f' (actual: {count})'
    )
    return enabled_models


@pytest.mark.asyncio
@pytest.mark.unit
class TestBaseDatasourceService:
    def test_controller(self, test_db) -> TestService:
        """Mock Guacamole controller for testing"""
        # for these tests: use a non-specialized controller
        controller = TestService(test_db)
        controller.model = GuacamoleSource
        return controller

    async def enabled_model(self, test_controller: TestService) -> GuacamoleSource:
        """Get the first enabled datasource"""
        return await get_first_status(test_controller, True)

    async def disabled_model(self, test_controller: TestService) -> GuacamoleSource:
        """Get the first disabled datasource"""
        return await get_first_status(test_controller, False)

    async def test_create_datasource(self, test_controller: TestService) -> None:
        pwd = 'test'
        args = GuacamoleCreate(**source_args(username='create_test', password=pwd))

        model = await test_controller.create_datasource(args)
        assert model.password != pwd, (
            f'Datasource passwords should be encrypted and not stored in plain text. (resulting password: {model.password}, input: {pwd})'
        )
        assert not model.enabled, (
            'The model should be disabled, not enabled by default to ensure only one model is ever enabled.'
        )

    async def test_enable_datasource(
        self, test_controller: TestService, disabled_model: GuacamoleSource
    ) -> None:
        """Test enabling a datasource"""

        newly_enabled = await test_controller.enable(disabled_model)

        assert newly_enabled.enabled, 'The datasource should be enabled'

        all_enabled = await assert_total_enabled_eq(1, test_controller)

        assert all_enabled[0].id == newly_enabled.id, (
            'The newly enabled datasource should be enabled after being enabled'
        )
        with pytest.raises(DatasourceToggleError):
            await test_controller.enable(newly_enabled)

    async def test_enable_enabled(
        self, test_controller: TestService, enabled_model: GuacamoleSource
    ) -> None:
        """Test enabling an already enabled datasource"""
        with pytest.raises(DatasourceToggleError):
            await test_controller.enable(enabled_model)

    async def test_disable_datasource(
        self, test_controller: TestService, enabled_model: GuacamoleSource
    ) -> None:
        # enabled_id = enabled_model.id
        updated = await test_controller.disable(enabled_model)
        assert not updated.enabled, 'The datasource should be disabled'
        await assert_total_enabled_eq(0, test_controller)

        # to prevent side effects and breaking features since the service commits transaction
        # and we need at least one enabled datasource to run the tests
        await test_controller.enable(updated)

    async def test_disable_disabled(
        self, test_controller: TestService, disabled_model: GuacamoleSource
    ) -> None:
        """Test disabling an already disabled datasource"""
        with pytest.raises(DatasourceToggleError):
            await test_controller.disable(disabled_model)

    async def test_toggle_datasource(
        self, test_controller: TestService, disabled_model: GuacamoleSource
    ) -> None:
        """Test toggling a datasource"""
        enabled = await test_controller.toggle(disabled_model)
        assert enabled.enabled, 'The datasource should be enabled'

        await assert_total_enabled_eq(1, test_controller)

        now_disabled = await test_controller.toggle(enabled)
        assert not now_disabled.enabled, 'The datasource should be disabled'

        await assert_total_enabled_eq(0, test_controller)

    async def test_update_by_id(
        self, test_controller: TestService, disabled_model: GuacamoleSource
    ) -> None:
        test_args = GuacamoleUpdate(username='updated', password='testing')

        assert test_args.username != disabled_model.username, 'sanity check failed'

        old_pwd = disabled_model.password
        args = test_args.serialize()

        updated = await test_controller.update_by_id(disabled_model.id, args)

        assert updated.username == test_args.username, (
            'The username did not change after updating'
        )
        assert test_args.password != updated.password, (
            'The password should be encrypted and not stored in plain text for both update and create'
        )

        assert old_pwd != updated.password, (
            'The password should be different after being updated'
        )

    async def test_update_by_id_with_enabled_included(
        self, test_controller: TestService, disabled_model: GuacamoleSource
    ) -> None:
        test_args = GuacamoleUpdate(username='guac_foo', password='testing').serialize()

        test_args['enabled'] = True

        updated = await test_controller.update_by_id(disabled_model.id, test_args)

        assert not updated.enabled, (
            'A datasources "enabled" flag should not change or allow to be updated via this '
            ' method and should only be allowed via the enable/disable/toggle methods to ensure. '
            ' multiple datasources are not enabled at once.'
        )

    async def test_delete_by_id(self, test_controller: TestService) -> None:
        """Test deleting a datasource"""
        new_model = await test_controller.create_datasource(
            GuacamoleCreate(**source_args('delete_test'))
        )
        assert new_model is not None, 'The datasource should be created'

        id = new_model.id

        assert test_controller.exists(test_controller.db, GuacamoleSource.id == id), (
            'The datasource should exist in the database after being created'
        )

        await test_controller.delete_by_id(new_model.id)

        assert not test_controller.exists(
            test_controller.db, GuacamoleSource.id == id
        ), 'The datasource should not exist in the database after being deleted'

    async def test_read_datasource_password(self, test_controller: TestService) -> None:
        pwd = 'read'
        new_model = await test_controller.create_datasource(
            GuacamoleCreate(**source_args('read_test', password=pwd))
        )
        assert new_model is not None and new_model.password != pwd, (
            'The datasource should ve been created and the password should ve been encrypted'
        )

        password = await test_controller.read_datasource_password(new_model)
        assert password == pwd, (
            'The password should be the same as the one used to create the datasource'
            f' (expect: {pwd}, actual: {password})'
        )
