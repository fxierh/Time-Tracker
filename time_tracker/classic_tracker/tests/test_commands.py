from unittest.mock import patch

from django.core.management import call_command
from django.db import OperationalError
from django.test import SimpleTestCase


# Decorator for mock test (i.e. mock the check function)
@patch('classic_tracker.management.commands.wait_for_db.Command.check')
class TestCustomCommands(SimpleTestCase):
    """Test custom manage.py commands"""

    @patch('time.sleep')
    def test_wait_for_db(self, patched_sleep, patched_check):
        """Test the custom wait_for_db manage.py command"""

        n_op_error = 5
        patched_check.side_effect = [OperationalError] * n_op_error + [None]
        call_command('wait_for_db', wait_interval=1.5)

        self.assertEqual(patched_check.call_count, n_op_error + 1)
        patched_check.assert_called_with(databases=['default'])
