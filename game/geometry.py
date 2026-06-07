from __future__ import annotations

from typing import Annotated

from pygame.math import Vector2

import math
import msgspec

type Radian = float


class Pose(msgspec.Struct, kw_only=True, frozen=True):
    """An object's position and rotation in a coordinate system."""

    position: Annotated[Vector2, msgspec.Meta(description="This object's position.")]
    rotation: Annotated[
        Radian,
        msgspec.Meta(
            description="This object's rotation, in Radians. +x is 0. Positive values rotate counter-clockwise."
        ),
    ]

    @property
    def forward_vector(self) -> Vector2:
        """Returns a unit vector pointing in the direction of this object, based on its ``rotation``."""
        return forward_vector(self.rotation)


def forward_vector(angle: Radian) -> Vector2:
    """Returns a unit vector pointing in the direction of the given angle."""
    return Vector2(x=math.cos(angle), y=math.sin(angle)).normalize()


def left_vector(angle: Radian) -> Vector2:
    """Returns a unit vector pointing to the left of the given angle."""
    return Vector2(x=-math.sin(angle), y=math.cos(angle)).normalize()


def vector_left_of(vector: Vector2) -> Vector2:
    """Returns a unit vector perpendicular to the given vector pointing to its left."""
    left_vector = Vector2(x=-vector.y, y=vector.x)
    # The provided vector may not be a normalized vector. Only normalize if needed since it's a slow operation.
    if not left_vector.is_normalized():
        left_vector.normalize_ip()
    return left_vector


def right_vector(angle: Radian) -> Vector2:
    """Returns a unit vector pointing to the right of the given angle."""
    return Vector2(x=math.sin(angle), y=-math.cos(angle)).normalize()


def vector_right_of(vector: Vector2) -> Vector2:
    """Returns a unit vector perpendicular to the given vector pointing to its right."""
    right_vector = Vector2(x=vector.y, y=-vector.x)
    # The provided vector may not be a normalized vector. Only normalize if needed since it's a slow operation.
    if not right_vector.is_normalized():
        right_vector.normalize_ip()
    return right_vector
