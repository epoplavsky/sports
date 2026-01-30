import cv2
import numpy as np
import supervision as sv
from typing import Tuple, Optional, List
from volleyball.config import CourtConfiguration
from common.core import MeasurementUnit


def _to_pixel(
    point: Tuple[float, float],
    scale: float,
    padding: int,
) -> Tuple[int, int]:
    """Scale court point to pixel space and apply padding."""
    return (
        int(round(point[0] * scale + padding)),
        int(round(point[1] * scale + padding)),
    )


def draw_court(
    config: CourtConfiguration,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 4,
    line_color: sv.Color = sv.Color.WHITE,
    background_color: sv.Color = sv.Color(224, 190, 139),
    attack_zone_color: Optional[sv.Color] = None,
    net_color: sv.Color = sv.Color.BLACK,
) -> np.ndarray:
    """Render a volleyball court to an image."""
    court_height_px = int(round(config.court_width * scale))
    court_length_px = int(round(config.court_length * scale))

    image = np.zeros(
        (court_height_px + 2 * padding, court_length_px + 2 * padding, 3),
        dtype=np.uint8,
    )
    image[:, :] = background_color.as_bgr()

    # Attack zone fill beneath lines
    if attack_zone_color is not None:
        left_attack_poly = np.array(
            [_to_pixel(config.vertices[i], scale, padding)
             for i in config.left_attack_zone_indexes],
            dtype=np.int32,
        )
        right_attack_poly = np.array(
            [_to_pixel(config.vertices[i], scale, padding)
             for i in config.right_attack_zone_indexes],
            dtype=np.int32,
        )
        cv2.fillPoly(image, [left_attack_poly], color=attack_zone_color.as_bgr())
        cv2.fillPoly(image, [right_attack_poly], color=attack_zone_color.as_bgr())

    # Court perimeter (sidelines and baselines)
    court_corners = [config.vertices[i] for i in config.court_corner_indexes]
    perimeter_points = np.array(
        [_to_pixel(corner, scale, padding) for corner in court_corners],
        dtype=np.int32,
    )
    cv2.polylines(
        image, [perimeter_points], isClosed=True,
        color=line_color.as_bgr(), thickness=line_thickness
    )

    # Center line (net line)
    center_start = _to_pixel(config.vertices[4], scale, padding)  # center bottom
    center_end = _to_pixel(config.vertices[5], scale, padding)  # center top
    cv2.line(image, center_start, center_end, line_color.as_bgr(), line_thickness)

    # Left attack line
    left_attack_start = _to_pixel(config.vertices[6], scale, padding)
    left_attack_end = _to_pixel(config.vertices[7], scale, padding)
    cv2.line(image, left_attack_start, left_attack_end, line_color.as_bgr(), line_thickness)

    # Right attack line
    right_attack_start = _to_pixel(config.vertices[8], scale, padding)
    right_attack_end = _to_pixel(config.vertices[9], scale, padding)
    cv2.line(image, right_attack_start, right_attack_end, line_color.as_bgr(), line_thickness)

    # Net representation (thicker line at center with posts)
    net_thickness = max(line_thickness * 2, 6)
    cv2.line(image, center_start, center_end, net_color.as_bgr(), net_thickness)

    # Net posts (small circles at ends of net)
    post_radius = line_thickness + 2
    cv2.circle(image, center_start, post_radius, net_color.as_bgr(), -1)
    cv2.circle(image, center_end, post_radius, net_color.as_bgr(), -1)

    # Service area indicators (optional dashed lines)
    if hasattr(config, '_service_area_depth_in_centimeters') and config._service_area_depth_in_centimeters > 0:
        # Left service area
        left_service_start = _to_pixel(config.vertices[10], scale, padding)
        left_service_end = _to_pixel(config.vertices[11], scale, padding)
        _draw_dashed_line(image, left_service_start, left_service_end,
                         line_color.as_bgr(), line_thickness)

        # Right service area
        right_service_start = _to_pixel(config.vertices[12], scale, padding)
        right_service_end = _to_pixel(config.vertices[13], scale, padding)
        _draw_dashed_line(image, right_service_start, right_service_end,
                         line_color.as_bgr(), line_thickness)

    return image


def _draw_dashed_line(
    image: np.ndarray,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Tuple[int, int, int],
    thickness: int,
    dash_length: int = 10,
    gap_length: int = 5,
) -> None:
    """Draw a dashed line between two points."""
    x1, y1 = start
    x2, y2 = end

    # Calculate total distance and direction
    dx = x2 - x1
    dy = y2 - y1
    distance = int(np.sqrt(dx * dx + dy * dy))

    if distance == 0:
        return

    # Normalize direction
    dx_norm = dx / distance
    dy_norm = dy / distance

    # Draw dashes
    current_distance = 0
    dash_pattern = dash_length + gap_length

    while current_distance < distance:
        # Start of dash
        dash_start_x = int(x1 + dx_norm * current_distance)
        dash_start_y = int(y1 + dy_norm * current_distance)

        # End of dash
        dash_end_distance = min(current_distance + dash_length, distance)
        dash_end_x = int(x1 + dx_norm * dash_end_distance)
        dash_end_y = int(y1 + dy_norm * dash_end_distance)

        cv2.line(image, (dash_start_x, dash_start_y),
                (dash_end_x, dash_end_y), color, thickness)

        current_distance += dash_pattern


def draw_made_and_miss_on_court(
    config: CourtConfiguration,
    made_xy: Optional[np.ndarray] = None,
    miss_xy: Optional[np.ndarray] = None,
    made_thickness: Optional[int] = None,
    miss_thickness: Optional[int] = None,
    made_color: sv.Color = sv.Color.from_hex("#007A33"),  # Green for successful plays
    miss_color: sv.Color = sv.Color.from_hex("#850101"),  # Red for errors
    made_size: int = 20,
    miss_size: int = 20,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Draw successful plays as circle outlines and errors as crosses."""
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    made_stroke = (
        made_thickness if made_thickness is not None else line_thickness
    )
    missed_stroke = (
        miss_thickness if miss_thickness is not None else line_thickness
    )

    def point_to_pixel(point: Tuple[float, float]) -> Tuple[int, int]:
        return _to_pixel(point, scale=scale, padding=padding)

    # Normalize inputs to iterable collections
    made_iter = (
        np.atleast_2d(made_xy) if made_xy is not None and made_xy.size > 0 else ()
    )
    miss_iter = (
        np.atleast_2d(miss_xy) if miss_xy is not None and miss_xy.size > 0 else ()
    )

    # Successful plays: circle border
    for point in made_iter:
        center_x, center_y = point_to_pixel(tuple(point))
        cv2.circle(
            img=court,
            center=(center_x, center_y),
            radius=made_size,
            color=made_color.as_bgr(),
            thickness=made_stroke,
        )

    # Errors: cross
    for point in miss_iter:
        center_x, center_y = point_to_pixel(tuple(point))
        x0, y0 = center_x - miss_size, center_y - miss_size
        x1, y1 = center_x + miss_size, center_y + miss_size
        cv2.line(court, (x0, y0), (x1, y1), miss_color.as_bgr(), missed_stroke)
        cv2.line(court, (x0, y1), (x1, y0), miss_color.as_bgr(), missed_stroke)

    return court


def draw_points_on_court(
    config: CourtConfiguration,
    xy: Optional[np.ndarray] = None,
    labels: Optional[list[str]] = None,
    fill_color: Optional[sv.Color] = sv.Color.BLACK,
    text_color: sv.Color = sv.Color.WHITE,
    edge_color: Optional[sv.Color] = sv.Color.WHITE,
    size: int = 30,
    edge_thickness: Optional[int] = None,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Draw points on the court.
    Points render as circles with optional fill, edge, and center labels.
    """
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    if xy is None or np.size(xy) == 0:
        return court

    pts = np.atleast_2d(xy)
    n = pts.shape[0]

    labels = labels if labels is not None else [None] * n
    if len(labels) < n:
        labels = list(labels) + [None] * (n - len(labels))

    stroke = edge_thickness if edge_thickness is not None else max(2, line_thickness // 2)
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = max(0.4, size / 28.0)
    font_thickness = max(1, size // 8)

    for i in range(n):
        cx, cy = _to_pixel(tuple(pts[i]), scale=scale, padding=padding)

        # Face (fill)
        if fill_color is not None:
            cv2.circle(
                img=court,
                center=(cx, cy),
                radius=size,
                color=fill_color.as_bgr(),
                thickness=-1,
                lineType=cv2.LINE_AA,
            )

        # Edge (outline)
        if edge_color is not None and stroke > 0:
            cv2.circle(
                img=court,
                center=(cx, cy),
                radius=size,
                color=edge_color.as_bgr(),
                thickness=stroke,
                lineType=cv2.LINE_AA,
            )

        # Label
        label = labels[i]
        if label is not None and str(label) != "":
            text = str(label)
            (tw, th), base = cv2.getTextSize(text, font, font_scale, font_thickness)
            tx = int(cx - tw / 2)
            ty = int(cy + th / 2)
            cv2.putText(
                img=court,
                text=text,
                org=(tx, ty),
                fontFace=font,
                fontScale=font_scale,
                color=text_color.as_bgr(),
                thickness=font_thickness,
                lineType=cv2.LINE_AA,
            )

    return court


def draw_paths_on_court(
    config: CourtConfiguration,
    paths: List[np.ndarray],
    color: Optional[sv.Color] = sv.Color.BLACK,
    thickness: Optional[int] = None,
    scale: float = 20,
    padding: int = 50,
    line_thickness: int = 6,
    court: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    Draw time-ordered paths as polylines in court coordinates.
    Each path is an array of shape (T, 2) with x, y in court units.
    NaN rows split a path into multiple segments.
    """
    if court is None:
        court = draw_court(
            config=config,
            scale=scale,
            padding=padding,
            line_thickness=line_thickness,
        )

    if not paths or color is None:
        return court

    stroke = thickness if thickness is not None else line_thickness
    bgr = color.as_bgr()

    def to_segments(pts: np.ndarray) -> list[np.ndarray]:
        pts = np.atleast_2d(pts).astype(float)
        segments = []
        cur = []
        for p in pts:
            if np.isnan(p).any():
                if len(cur) > 0:
                    segments.append(np.asarray(cur, dtype=float))
                    cur = []
            else:
                cur.append(p)
        if len(cur) > 0:
            segments.append(np.asarray(cur, dtype=float))
        return segments

    for path in paths:
        if path is None or np.size(path) == 0:
            continue

        for seg in to_segments(path):
            if seg.shape[0] >= 2:
                poly = np.array(
                    [[_to_pixel((float(x), float(y)), scale, padding) for x, y in seg]],
                    dtype=np.int32,
                )
                cv2.polylines(
                    img=court,
                    pts=poly,
                    isClosed=False,
                    color=bgr,
                    thickness=stroke,
                    lineType=cv2.LINE_AA,
                )
            elif seg.shape[0] == 1:
                cx, cy = _to_pixel((float(seg[0, 0]), float(seg[0, 1])), scale, padding)
                cv2.circle(
                    img=court,
                    center=(cx, cy),
                    radius=max(1, stroke // 2),
                    color=bgr,
                    thickness=-1,
                    lineType=cv2.LINE_AA,
                )

    return court