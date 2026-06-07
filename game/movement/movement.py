"""Maneuver execution: turn a ship's pose plus a chosen maneuver into the
poses it sweeps through and the final pose where it comes to rest.
"""

from enum import Enum, auto
from functools import cache
import math

from types import MappingProxyType
from typing import Final

from pygame.math import Vector2

from game.geometry import Pose, forward_vector, left_vector, right_vector
from game.measurement import Size
from game.measurement.measurement import Distance
from game.movement import Maneuver, ManeuverBearing


class _ManeuverBearingArchetype(Enum):
    STATIONARY = auto()
    STRAIGHT = auto()
    BANK = auto()
    TURN = auto()

    @staticmethod
    def from_bearing(bearing: ManeuverBearing) -> '_ManeuverBearingArchetype':
        """Map a maneuver bearing to the archetype used to perform the maneuver."""
        match bearing:
            case ManeuverBearing.STATIONARY:
                return _ManeuverBearingArchetype.STATIONARY
            case (
                ManeuverBearing.STRAIGHT
                | ManeuverBearing.REVERSE_STRAIGHT
                | ManeuverBearing.KOIOGRAN_TURN
            ):
                return _ManeuverBearingArchetype.STRAIGHT
            case (
                ManeuverBearing.BANK_LEFT
                | ManeuverBearing.BANK_RIGHT
                | ManeuverBearing.REVERSE_BANK_LEFT
                | ManeuverBearing.REVERSE_BANK_RIGHT
                | ManeuverBearing.SEGNORS_LOOP_LEFT
                | ManeuverBearing.SEGNORS_LOOP_RIGHT
            ):
                return _ManeuverBearingArchetype.BANK
            case (
                ManeuverBearing.TURN_LEFT
                | ManeuverBearing.TURN_RIGHT
                | ManeuverBearing.TALLON_ROLL_LEFT
                | ManeuverBearing.TALLON_ROLL_RIGHT
            ):
                return _ManeuverBearingArchetype.TURN
            case _:
                raise ValueError(f'Unsupported bearing for archetype lookup: {bearing}')


@cache
def _is_reverse_maneuver(maneuver: Maneuver) -> bool:
    """Whether the maneuver is a reverse maneuver, which traces the same path
    backwards and has the guide on the back edge instead of the front."""
    return maneuver.bearing in set(
        [
            ManeuverBearing.REVERSE_STRAIGHT,
            ManeuverBearing.REVERSE_BANK_LEFT,
            ManeuverBearing.REVERSE_BANK_RIGHT,
        ]
    )


@cache
def _is_clockwise_arc(maneuver: Maneuver) -> bool:
    if _ManeuverBearingArchetype.from_bearing(maneuver.bearing) not in set(
        [
            _ManeuverBearingArchetype.BANK,
            _ManeuverBearingArchetype.TURN,
        ]
    ):
        raise ValueError(f'Cannot determine arc direction for non-arc maneuver: {maneuver}')

    """Whether the maneuver is a clockwise arc, which has the guide on the right
    edge instead of the left."""
    return maneuver.bearing in set(
        [
            ManeuverBearing.BANK_RIGHT,
            ManeuverBearing.REVERSE_BANK_RIGHT,
            ManeuverBearing.SEGNORS_LOOP_RIGHT,
            ManeuverBearing.TURN_RIGHT,
            ManeuverBearing.TALLON_ROLL_RIGHT,
        ]
    )


@cache
def _straight_maneuver_length(*, maneuver: Maneuver) -> Distance:
    """The distance along the maneuver's guide edge from start to end."""
    archetype = _ManeuverBearingArchetype.from_bearing(maneuver.bearing)
    speed = maneuver.speed

    match archetype:
        case _ManeuverBearingArchetype.STATIONARY:
            return 0.0
        case _ManeuverBearingArchetype.STRAIGHT:
            # the speed-1 straight maneuver length, used to derive the others by scaling
            base_speed = 40.0
            if speed < 1 or speed > 5:
                raise ValueError(
                    f'Unsupported speed for straight maneuver: {speed}. Must be in [1, 5].'
                )
            return base_speed * speed
        case _ManeuverBearingArchetype.BANK | _ManeuverBearingArchetype.TURN:
            raise ValueError(
                f'Cannot lookup straight length for non-straight maneuver archetype: {archetype}, base maneuver bearing: {maneuver.bearing}'
            )
        case _:
            raise ValueError(f'Unsupported archetype for length lookup: {archetype}')


@cache
def _arc_maneuver_radius(*, maneuver: Maneuver) -> Distance:
    """The radius of the circular arc followed by the maneuver's guide edge. Only
    applies to turning maneuvers, straight maneuvers return 0."""
    archetype = _ManeuverBearingArchetype.from_bearing(maneuver.bearing)
    speed = maneuver.speed

    match archetype:
        case _ManeuverBearingArchetype.BANK:
            if speed == 1:
                return 85.0
            elif speed == 2:
                return 132.0
            elif speed == 3:
                return 183.0
            else:
                raise ValueError(
                    f'Unsupported speed for bank maneuver: {speed}. Must be in [1, 3].'
                )
        case _ManeuverBearingArchetype.TURN:
            if speed == 1:
                return 37.0
            elif speed == 2:
                return 62.0
            elif speed == 3:
                return 89.0
            else:
                raise ValueError(
                    f'Unsupported speed for turn maneuver: {speed}. Must be in [1, 3].'
                )
        case _ManeuverBearingArchetype.STRAIGHT | _ManeuverBearingArchetype.STATIONARY:
            raise ValueError(
                f'Cannot lookup arc radius for non-turning maneuver archetype: {archetype}, base maneuver bearing: {maneuver.bearing}'
            )
        case _:
            raise ValueError(
                f'Unsupported archetype for radius lookup: {archetype}, base maneuver bearing: {maneuver.bearing}'
            )


ANGLE_SWEEPS: Final = MappingProxyType(
    {
        _ManeuverBearingArchetype.BANK: math.pi / 4,
        _ManeuverBearingArchetype.TURN: math.pi / 2,
    }
)


def _angle_sweep(*, bearing_archetype: _ManeuverBearingArchetype) -> float:
    """The angle swept by the maneuver's guide edge along the distance of the maneuver.
    This is only used for turning maneuvers, non-turn maneuvers raise a ValueError."""
    try:
        return ANGLE_SWEEPS[bearing_archetype]
    except KeyError:
        raise ValueError(f'Unsupported archetype for angle sweep lookup: {bearing_archetype}')


def _straight_maneuver_poses(
    *, starting_point: Vector2, heading: float, length: float, travel_sign: float, num_samples: int
) -> list[Pose]:
    """Sample the guide edge moving in a straight line. Heading is constant."""
    forward = forward_vector(angle=heading)
    sample_range_max = num_samples if num_samples > 1 else 2
    return [
        Pose(
            position=Vector2(
                x=starting_point.x + travel_sign * forward.x * length * i / (sample_range_max - 1),
                y=starting_point.y + travel_sign * forward.y * length * i / (sample_range_max - 1),
            ),
            rotation=heading,
        )
        for i in range(sample_range_max)
    ]


def _arc_maneuver_poses(
    *,
    starting_point: Vector2,
    heading: float,
    radius: float,
    sweep: float,
    is_clockwise_arc: bool,
    travel_sign: float,
    num_samples: int,
) -> list[Pose]:
    """Sample the guide template following a circular arc, staying tangent throughout.

    ``travel_sign`` is +1 for forward maneuvers and -1 for reverse (which traces the same
    distance backwards). ``num_samples`` is how many points along the arc to sample. This
    will always return at least the start and end samples regardless of the value passed in.
    """
    # Counter-clockwise rotations increase the angle as it sweeps across the arc. Clockwise rotations
    # decrease the angle as it sweeps across the arc.
    rotation_sign = -1.0 if is_clockwise_arc else 1.0
    # CCW rotations have the center point of the rotation to the left of starting_point. CW rotations
    # have a center point to the right of starting_point. Left and right vectors are normalized.
    perpindicular = right_vector(angle=heading) if is_clockwise_arc else left_vector(angle=heading)
    center_point = Vector2(
        x=starting_point.x + (radius * perpindicular.x),
        y=starting_point.y + (radius * perpindicular.y),
    )
    arc_vector = starting_point - center_point
    poses: list[Pose] = []
    # Ensure there's at least two samples, the start and end Poses.
    sample_range_max = num_samples if num_samples > 1 else 2
    for i in range(sample_range_max):
        # normalized index in [0.0, 1.0]
        fraction = float(i) / float(sample_range_max - 1)
        rotation_amount = travel_sign * rotation_sign * sweep * fraction
        rotated_point = arc_vector.rotate_rad(rotation_amount)
        # Add back the center point to translate from rotation frame of reference to world coordinate
        position_in_worldspace = rotated_point + center_point
        # The rotation amount around the circle is the same as the rotation of the tangent vector.
        tangent_at_point = heading + rotation_amount
        poses.append(Pose(position=position_in_worldspace, rotation=tangent_at_point))
    return poses


def _poses_along_maneuver_path(
    *, starting_point: Vector2, heading: float, maneuver: Maneuver, num_samples: int
) -> list[Pose]:
    """Dispatch a maneuver to the path its guide edge traces along the distance."""
    bearing_archetype = _ManeuverBearingArchetype.from_bearing(maneuver.bearing)
    travel_sign = -1.0 if _is_reverse_maneuver(maneuver) else 1.0

    match bearing_archetype:
        case _ManeuverBearingArchetype.STATIONARY | _ManeuverBearingArchetype.STRAIGHT:
            maneuver_length = _straight_maneuver_length(maneuver=maneuver)
            return _straight_maneuver_poses(
                starting_point=starting_point,
                heading=heading,
                length=maneuver_length,
                travel_sign=travel_sign,
                num_samples=num_samples,
            )
        case _ManeuverBearingArchetype.BANK | _ManeuverBearingArchetype.TURN:
            radius = _arc_maneuver_radius(maneuver=maneuver)
            angle_sweep = _angle_sweep(bearing_archetype=bearing_archetype)
            is_clockwise_arc = _is_clockwise_arc(maneuver)
            return _arc_maneuver_poses(
                starting_point=starting_point,
                heading=heading,
                radius=radius,
                sweep=angle_sweep,
                is_clockwise_arc=is_clockwise_arc,
                travel_sign=travel_sign,
                num_samples=num_samples,
            )
        case _:
            raise ValueError(f'Unsupported bearing for path generation: {bearing_archetype}')


def _post_rotation(bearing: ManeuverBearing) -> float:
    """In-place heading change applied after the base maneuver, for the
    rotate-on-the-spot maneuvers (Koiogran / Segnor's loop / Tallon roll)."""
    match bearing:
        case (
            ManeuverBearing.KOIOGRAN_TURN
            | ManeuverBearing.SEGNORS_LOOP_LEFT
            | ManeuverBearing.SEGNORS_LOOP_RIGHT
        ):
            return math.pi
        case ManeuverBearing.TALLON_ROLL_LEFT:
            return math.pi / 2
        case ManeuverBearing.TALLON_ROLL_RIGHT:
            return -math.pi / 2
        case _:
            return 0.0


# --- Public API ------------------------------------------------------------
def maneuver_path(
    *,
    start: Pose,
    maneuver: Maneuver,
    base: Size,
    num_samples: int,
) -> list[Pose]:
    """Return the base-centre poses the ship passes through for `maneuver`.

    The list runs from the starting pose to the final resting pose. The final
    pose will have the edge of the ship's base aligned with the end of the
    maneuver template, and the ship will be rotated to match the ending state
    of the maneuver.
    """
    if maneuver.bearing is ManeuverBearing.STATIONARY:
        return [start]

    forward = start.forward_vector
    # The guide is placed at the front edge for forward maneuvers, the back edge for reverse.
    guide_dir = -1.0 if _is_reverse_maneuver(maneuver) else 1.0
    distance_to_maneuver_edge = Vector2(
        x=(forward.x * (base.height / 2)) * guide_dir, y=(forward.y * (base.height / 2)) * guide_dir
    )
    starting_point = start.position + distance_to_maneuver_edge

    maneuver_poses = _poses_along_maneuver_path(
        starting_point=starting_point,
        heading=start.rotation,
        maneuver=maneuver,
        num_samples=num_samples,
    )

    # Move the ship by a half height of the base to put the edge of the base at the edge of the maneuver
    # template.
    last_pose = maneuver_poses[-1]
    last_pose_forward_vector = last_pose.forward_vector
    final_position = last_pose.position + (
        (last_pose_forward_vector * (base.height / 2)) * guide_dir
    )
    maneuver_poses.append(Pose(position=final_position, rotation=last_pose.rotation))

    # TODO - Add step for player to align the center line of the ship to the top, middle, bottom of the
    # maneuver template for Tallon Roll and Barrel Roll.
    # If the maneuver has a final rotation (like a Tallon Roll), apply it as the final step.
    special_maneuver_rotation_amount = _post_rotation(maneuver.bearing)
    if special_maneuver_rotation_amount:
        last_pose = maneuver_poses[-1]
        final_rotation = last_pose.rotation + special_maneuver_rotation_amount
        final_rotated_pose = Pose(position=last_pose.position, rotation=final_rotation)
        maneuver_poses.append(final_rotated_pose)
    return maneuver_poses
