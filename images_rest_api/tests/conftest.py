from pytest_factoryboy import register

from .factories import (
    ThumbnailSizeFactory,
    AccountTypeFactory,
    CustomUserFactory,
    UserImageFactory,
)

register(ThumbnailSizeFactory)
register(AccountTypeFactory)
register(CustomUserFactory)
register(UserImageFactory)
