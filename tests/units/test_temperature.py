import pytest

from local_tuya_domoticz_tools.units.base import UnitValues
from local_tuya_domoticz_tools.units.temperature import temperature_unit


@pytest.fixture()
def unit_kwargs(mocker):
    unit = mocker.patch("local_tuya_domoticz_tools.units.temperature.Unit")
    temperature_unit(1, "", 1)
    unit.assert_called_once()
    return unit.call_args[1]


def test_to_unit_values(unit_kwargs):
    to_unit_values = unit_kwargs["to_unit_values"]
    assert to_unit_values(10.2) == UnitValues(1, "10.2")
