import datetime
from unittest.mock import patch

import pytest

from standupbrain.shared import get_previous_workday


@pytest.mark.parametrize(
    ('today_weekday', 'expected_days_back'),
    [
        (0, 3),
        (1, 1),
        (2, 1),
        (3, 1),
        (4, 1),
        (5, 1),
        (6, 1),
    ],
)
def test_get_previous_workday(today_weekday: int, expected_days_back: int) -> None:
    mock_today = datetime.datetime(2025, 1, 6 + today_weekday)
    with patch('standupbrain.shared.datetime.datetime') as mock_dt:
        mock_dt.now.return_value = mock_today
        result = get_previous_workday()
        assert result == mock_today - datetime.timedelta(days=expected_days_back)
