CAN_MODERATE_VERSION = "can_moderate_version"
CAN_SET_VIDEO_AS_MODERATED = "can_set_video_as_moderated"
CAN_UNSET_VIDEO_AS_MODERATED = "can_unset_video_as_moderated"

UNMODERATED = "not__under_moderation"
WAITING_MODERATION = "waiting_moderation"
APPROVED =   "approved"
REJECTED = "rejected"

MODERATION_STATUSES = (
    (UNMODERATED , "not__under_moderation",),
    (WAITING_MODERATION , "waiting_moderation",),
    (APPROVED,   "approved"),
    (REJECTED,  "rejected"),
)

SUBJECT_EMAIL_VERSION_REJECTED = "Your version for %s was declined"
