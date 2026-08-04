from enum import IntEnum


class AttemptStatus(IntEnum):
    IN_PROGRESS = 0
    EXPIRED = 1
    SUBMITTED = 2
    FORCE_SUBMITTED = 3