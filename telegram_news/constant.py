# -*- coding: UTF-8 -*-

MAX_MESSAGE_LENGTH = 4096
MAX_CAPTION_LENGTH = 1024
MAX_THUMB_SIZE = 200
MAX_URL_IMAGE_SIZE = 5 * 1024
MAX_URL_VIDEO_SIZE = 20 * 1024
MAX_IMAGE_SIZE = 10 * 1024  # May be changed in the future.
MAX_VIDEO_SIZE = 50 * 1024  # May be changed in the future.
MAX_PHOTOSIZE_UPLOAD = int(10E6)  # (10MB)
MAX_VIDEOSIZE_UPLOAD = int(20E6)  # (20MB)

MAX_MESSAGES_PER_SECOND_PER_CHAT = 1
MAX_MESSAGES_PER_SECOND = 30
MAX_MESSAGES_PER_MINUTE_PER_GROUP = 20

MAX_MEDIA_PER_MEDIAGROUP = 10

ALL_METHOD = [
    'getMe',
    'sendMessage',
    'forwardMessage',
    'sendPhoto',
    'sendAudio',
    'sendDocument',
    'sendVideo',
    'sendAnimation',
    'sendVoice',
    'sendVideoNote',
    'sendMediaGroup',
    'sendLocation',
    'editMessageLiveLocation',
    'stopMessageLiveLocation',
    'sendVenue',
    'sendContact',
    'sendPoll',
    'sendDice',
    'sendChatAction',
    'getUserProfilePhotos',
    'getFile',
    'kickChatMember',
    'unbanChatMember',
    'restrictChatMember',
    'promoteChatMember',
    'setChatAdministratorCustomTitle',
    'setChatPermissions',
    'exportChatInviteLink',
    'setChatPhoto',
    'deleteChatPhoto',
    'etChatTitle',
    'setChatDescription',
    'pinChatMessage',
    'unpinChatMessage',
    'leaveChat',
    'getChat',
    'getChatAdministrators',
    'getChatMembersCount',
    'getChatMember',
    'setChatStickerSet',
    'deleteChatStickerSet',
    'answerCallbackQuery',
    'setMyCommands',
    'getMyCommands'
]


AVAILABLE_METHOD = [
    'sendMessage',
    'sendPhoto',
    'sendVideo',
    'sendMediaGroup'
]
