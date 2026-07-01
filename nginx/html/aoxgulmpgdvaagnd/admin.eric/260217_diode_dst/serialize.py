import construct as cs
import enum
import random

class BlobType(enum.IntEnum):
    WEAPON_OPEN_SESSION = 0,
    WEAPON_CLOSE_SESSION = 1,
    WEAPONS_MSG = 2,
    UPDATE_WALLPAPER = 3,
    UPDATE_SIG_KEY = 4,
    UPDATE_SIG_EXE = 5,
    UTILS_SLEEP = 6,
    UTILS_CLEAR_SCREEN = 7,
    UTILS_GET_FLAG_STEP3 = 8,
    UPDATE_USER_DB = 9,


pkg_t = cs.Struct(
    "magic" / cs.Const(b"MCRY"),
    "body" / cs.Struct(
        "count" / cs.Int8ul,
        "blobs" / cs.Array(cs.this.count, cs.Struct(
            "magic_blob" / cs.Const(b"AKNG"),
            "size" / cs.Int32ul,
            "type" / cs.Enum(cs.Int32ul, BlobType),
            "data" / cs.Array(cs.this.size, cs.Byte),
        ))
    )
)

TAGS_OFFSET = 48

sstic_arch_t = cs.Struct(
    "magic" / cs.Int64ul,
    "crc64" / cs.Int64ul,
    "pkg_offset" /cs.Int64ul,
    "pkg_decompressed_size" / cs.Int64ul,
    "sig_offset" / cs.Int64ul,
    "secret_offset" / cs.Int64ul,
    "tags" / cs.Bytes(lambda ctx: ctx.pkg_offset - TAGS_OFFSET),
    "pkg" /  cs.Bytes(lambda ctx: ctx.sig_offset - ctx.pkg_offset),
    "sig" / cs.Bytes(lambda ctx: ctx.secret_offset - ctx.sig_offset),
    "secret" / cs.GreedyBytes
)
