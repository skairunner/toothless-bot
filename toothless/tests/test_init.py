from toothless import Toothless, ConfigError
import pytest

def try_supply_long_command_prefix():
    Toothless([], '//')

def test_rejects_long_command_prefixes():
    with pytest.raises(ConfigError):
        try_supply_long_command_prefix()
