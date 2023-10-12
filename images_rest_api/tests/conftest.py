from pytest_factoryboy import register
import pytest

from .factories import (
    ThumbnailSizeFactory,
    AccountTypeFactory,
    CustomUserFactory,
    UserImageFactory,
)
pytestmark = pytest.mark.django_db

register(ThumbnailSizeFactory)
register(AccountTypeFactory)
register(CustomUserFactory)
register(UserImageFactory)
