from enum import Enum


class InvitationStatus(str, Enum):
    INVITED = 'invited'
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    DECLINED_BY_USER = 'declined_by_user'
    DECLINED_BY_COMPANY = 'declined_by_company'


class InvitationType(str, Enum):
    INVITE = 'invite'
    REQUEST = 'request'


class MemberStatus(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    OWNER = 'owner'


