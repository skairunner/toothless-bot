from toothless import tokens as t
from datetime import datetime, timedelta, timezone


# The maximum permitted error between expected & actual time
EPSILON = 1

# Test that "for 10 seconds" is parsed similarly to "in 10 seconds"
def test_date_proto_relative_for():
    parsed = t.DateProto.verify('for 59 seconds')
    expected = datetime.now(timezone.utc) + timedelta(seconds=59)
    diff = expected - parsed
    assert -EPSILON < diff.total_seconds() < EPSILON
