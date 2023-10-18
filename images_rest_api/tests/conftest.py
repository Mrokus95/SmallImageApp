import pytest
from imageapp import settings 
from pytest_factoryboy import register

from .factories import (AccountTypeFactory, CustomUserFactory,
                        ThumbnailSizeFactory, UserImageFactory)

pytestmark = pytest.mark.django_db

register(ThumbnailSizeFactory)
register(AccountTypeFactory)
register(CustomUserFactory)
register(UserImageFactory)
