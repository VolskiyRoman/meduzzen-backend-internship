from enum import Enum


class InvitationStatus(Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    PROMOTED = 'promoted'
