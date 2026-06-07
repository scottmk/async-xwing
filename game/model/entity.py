from game.geometry import Pose, Radian
from pygame.math import Vector2

import msgspec


class Entity(msgspec.Struct, kw_only=True):
    """An entity on the game board which has a position and rotation."""

    id: str
    """The unique identifier for this entity."""
    pose: Pose
    """The position and rotation for this entity."""

    @property
    def position(self) -> Vector2:
        return self.pose.position

    @property
    def rotation(self) -> Radian:
        return self.pose.rotation

    def forward_vector(self) -> Vector2:
        """Returns a unit vector pointing in the direction this entity is facing."""
        return self.pose.forward_vector
