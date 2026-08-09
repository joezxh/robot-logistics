from rcs.controllers._common import CommandQueue
from rcs.state.command import Command, CommandType


def test_command_queue_idempotent():
    q = CommandQueue(maxsize=16)
    cmd = Command(type=CommandType.STOP)
    assert q.push(cmd) is True
    assert q.push(cmd) is False


def test_command_queue_bounded():
    q = CommandQueue(maxsize=3)
    for _ in range(3):
        assert q.push(Command(type=CommandType.STOP)) is True
    assert q.push(Command(type=CommandType.STOP)) is False
