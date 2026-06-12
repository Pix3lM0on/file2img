"""Pixel coordinate patterns."""

from collections.abc import Iterator


def iter_pattern(name: str, width: int, height: int) -> Iterator[tuple[int, int]]:
    if width <= 0 or height <= 0:
        return

    if name == "row":
        yield from _row(width, height)
    elif name == "row_reverse":
        yield from reversed(list(_row(width, height)))
    elif name == "spiral":
        yield from _spiral(width, height)
    elif name == "spiral_reverse":
        yield from reversed(list(_spiral(width, height)))
    else:
        choices = ", ".join(available_patterns())
        raise ValueError(f"unknown pattern {name!r}; try one of: {choices}")


def available_patterns() -> tuple[str, ...]:
    return ("spiral", "spiral_reverse", "row", "row_reverse")


def _row(width: int, height: int) -> Iterator[tuple[int, int]]:
    for y in range(height):
        for x in range(width):
            yield x, y


def _spiral(width: int, height: int) -> Iterator[tuple[int, int]]:
    left = 0
    right = width - 1
    top = 0
    bottom = height - 1

    while left <= right and top <= bottom:
        for x in range(left, right + 1):
            yield x, top
        top += 1

        for y in range(top, bottom + 1):
            yield right, y
        right -= 1

        if top <= bottom:
            for x in range(right, left - 1, -1):
                yield x, bottom
            bottom -= 1

        if left <= right:
            for y in range(bottom, top - 1, -1):
                yield left, y
            left += 1
