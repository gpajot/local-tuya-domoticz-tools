import sys
from logging import NullHandler
from typing import Any

import pytest
from local_tuya import Device, ProtocolConfig, Version

from local_tuya_domoticz_tools.plugin.metadata import PluginMetadata
from local_tuya_domoticz_tools.plugin.plugin import Plugin
from local_tuya_domoticz_tools.types import DomoticzEx
from local_tuya_domoticz_tools.units import UnitId
from local_tuya_domoticz_tools.units.base import UnitCommand
from local_tuya_domoticz_tools.units.manager import UnitManager


class TheUnitId(UnitId):
    ONE = 1
    TWO = 2


@pytest.fixture()
def domoticz(mocker):
    return mocker.patch(
        "local_tuya_domoticz_tools.plugin.plugin.DomoticzEx", spec=DomoticzEx
    )


@pytest.fixture()
def metadata(mocker):
    metadata = mocker.Mock(spec=PluginMetadata)
    metadata.package = "test"
    return metadata


@pytest.fixture()
def device(mocker):
    return mocker.MagicMock(spec=Device)


@pytest.fixture()
def units(mocker):
    return mocker.Mock()


@pytest.fixture()
def manager(mocker):
    return mocker.Mock(spec=UnitManager)


@pytest.fixture()
def manager_init(mocker, manager):
    return mocker.patch(
        "local_tuya_domoticz_tools.plugin.plugin.UnitManager",
        return_value=manager,
    )


@pytest.fixture()
def on_start(mocker, device):
    return mocker.Mock(return_value=device)


@pytest.fixture()
def parameters():
    return {
        "Name": "test",
        "Username": "id",
        "Address": "localhost",
        "Port": "6666",
        "Password": "key",
        "Mode4": "3.3",
        "Mode5": "one",
        "Mode6": "no",
    }


@pytest.fixture()
def plugin(
    mocker, metadata, units, parameters, manager, manager_init, on_start, domoticz
):
    mocker.patch(
        "local_tuya_domoticz_tools.plugin.plugin.LOG_HANDLER", new=NullHandler()
    )
    plugin: Plugin[Any] = Plugin("test", on_start, TheUnitId)
    _device = mocker.Mock()
    _device.Units = units
    plugin.start(parameters, {"test": _device})
    try:
        yield plugin
    finally:
        plugin.stop()


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="requires python3.8 or higher for AsyncMock",
)
@pytest.mark.usefixtures("plugin")
def test_start(
    plugin,
    parameters,
    manager,
    manager_init,
    on_start,
    device,
    domoticz,
    units,
):
    device.__aenter__.assert_awaited_once()
    domoticz.Heartbeat.assert_called_once_with(15)
    domoticz.Debugging.assert_called_once_with(0)
    manager_init.assert_called_once_with(
        name="test",
        units=units,
        included_units={TheUnitId.ONE},
    )
    on_start.assert_called_once_with(
        ProtocolConfig(
            id_="id",
            address="localhost",
            port=6666,
            key=b"key",
            version=Version.v33,
        ),
        parameters,
        manager,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="requires python3.8 or higher for AsyncMock",
)
def test_on_command(plugin, manager):
    plugin.on_command(1, UnitCommand("cmd", 10.2, ""))
    plugin.stop()  # drain pool

    manager.on_command.assert_awaited_once_with(1, UnitCommand("cmd", 10.2, ""))
