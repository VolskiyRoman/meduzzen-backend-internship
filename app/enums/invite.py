from enum import Enum


class InvitationStatus(str, Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    PROMOTED = 'promoted'
