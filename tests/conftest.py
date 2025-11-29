import random
import pytest


skip_90_percent_for_slower_tests = pytest.mark.skipif(
    random.random() > 0.1,  # noqa: PLR2004
    reason='runs 10 percent of the time',
)
