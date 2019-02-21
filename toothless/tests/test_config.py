from toothless.toothless import Toothless, ConfigError
import pytest
import mock

def test_cmd_prefix_cannot_be_long():
    with mock.patch(
            'toothless.configwrapper.COMMAND_PREFIX', '//'):
        with pytest.raises(ConfigError):
            Toothless()
