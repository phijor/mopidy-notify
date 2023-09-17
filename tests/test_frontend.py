from mopidy.models import Image
from mopidy_notify.frontend import find_preferred_image


def test_find_preferred_image_empty():
    assert find_preferred_image([], preferred_size=64) is None


def image(width) -> Image:
    return Image(uri="http://invalid./", width=width, height=width)


def test_find_preferred_image_singleton():
    img = image(50)
    assert find_preferred_image([img], preferred_size=64) is img


def test_find_preferred_image_singleton_large():
    img = image(100)
    assert find_preferred_image([img], preferred_size=64) is img


def test_find_preferred_image_width_all_none():
    img = find_preferred_image([image(None), image(None)], preferred_size=64)
    assert img is not None
    assert img.width is None


def test_find_preferred_image_width_some_none():
    img = find_preferred_image([image(42), image(None)], preferred_size=64)
    assert img is not None
    assert img.width == 42


def test_find_preferred_image_width_exact():
    img = find_preferred_image([image(63), image(64), image(65)], preferred_size=64)
    assert img is not None
    assert img.width == 64
