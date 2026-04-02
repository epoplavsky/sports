from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING
from enum import Enum
from typing import Dict, List, Tuple

from sports.common.core import MeasurementUnit

CENTIMETERS_PER_FOOT = Decimal("30.48")


class League(Enum):
    NCAA_WOMEN = "ncaa_women"
    NCAA_MEN = "ncaa_men"


# presets stored in centimeters
PRESETS_CENTIMETERS: Dict[League, Dict[str, int]] = {
    League.NCAA_WOMEN: dict(
        court_width=900,  # 9m
        court_length=1800,  # 18m
        attack_line_distance=300,  # 3m from center line
        service_area_width=900,  # full width of court
        service_area_depth=900,  # depth behind baseline for service area
        net_height=224,  # 2.24m for women
        net_width=100,  # 1m
        center_line_width=5,  # 5cm
        sideline_width=5,  # 5cm
        attack_line_width=5,  # 5cm
        service_line_distance=900,  # distance from baseline to back of service area
    ),
    League.NCAA_MEN: dict(
        court_width=900,  # 9m
        court_length=1800,  # 18m
        attack_line_distance=300,  # 3m from center line
        service_area_width=900,  # full width of court
        service_area_depth=900,  # depth behind baseline for service area
        net_height=243,  # 2.43m for men
        net_width=100,  # 1m
        center_line_width=5,  # 5cm
        sideline_width=5,  # 5cm
        attack_line_width=5,  # 5cm
        service_line_distance=900,  # distance from baseline to back of service area
    ),
}


@dataclass
class CourtConfiguration:
    """Configure volleyball court dimensions for NCAA leagues.
    Provides court measurements in centimeters or feet with proper unit
    conversion and vertex/edge data for court visualization.

    Args:
        league: The volleyball league standard to use (`League.NCAA_WOMEN` or
            `League.NCAA_MEN`).
        measurement_unit: Output unit for measurements
            (`MeasurementUnit.CENTIMETERS` or `MeasurementUnit.FEET`).

    Examples:
        ```
        from sports import MeasurementUnit
        from sports.volleyball import CourtConfiguration, League

        # Create NCAA Women's court configuration in centimeters
        women_config = CourtConfiguration(
            league=League.NCAA_WOMEN,
            measurement_unit=MeasurementUnit.CENTIMETERS
        )
        print(f"Court width: {women_config.court_width} cm")
        # Court width: 900.0 cm
        print(f"Net height: {women_config.net_height} cm")
        # Net height: 224.0 cm
        ```
    """
    league: League
    measurement_unit: MeasurementUnit = MeasurementUnit.CENTIMETERS

    # internal values in centimeters
    _court_width_in_centimeters: int = field(init=False)
    _court_length_in_centimeters: int = field(init=False)
    _attack_line_distance_in_centimeters: int = field(init=False)
    _service_area_width_in_centimeters: int = field(init=False)
    _service_area_depth_in_centimeters: int = field(init=False)
    _net_height_in_centimeters: int = field(init=False)
    _net_width_in_centimeters: int = field(init=False)
    _center_line_width_in_centimeters: int = field(init=False)
    _sideline_width_in_centimeters: int = field(init=False)
    _attack_line_width_in_centimeters: int = field(init=False)
    _service_line_distance_in_centimeters: int = field(init=False)

    def __post_init__(self) -> None:
        preset = PRESETS_CENTIMETERS[self.league]
        self._court_width_in_centimeters = preset["court_width"]
        self._court_length_in_centimeters = preset["court_length"]
        self._attack_line_distance_in_centimeters = preset["attack_line_distance"]
        self._service_area_width_in_centimeters = preset["service_area_width"]
        self._service_area_depth_in_centimeters = preset["service_area_depth"]
        self._net_height_in_centimeters = preset["net_height"]
        self._net_width_in_centimeters = preset["net_width"]
        self._center_line_width_in_centimeters = preset["center_line_width"]
        self._sideline_width_in_centimeters = preset["sideline_width"]
        self._attack_line_width_in_centimeters = preset["attack_line_width"]
        self._service_line_distance_in_centimeters = preset["service_line_distance"]

    # conversion helpers
    def _to_output_unit_rounded_up(self, value_in_centimeters: float) -> float:
        value = Decimal(str(value_in_centimeters))
        if self.measurement_unit == MeasurementUnit.FEET:
            value = value / CENTIMETERS_PER_FOOT
        return float(value.quantize(Decimal("0.01"), rounding=ROUND_CEILING))

    # public properties in the selected unit
    @property
    def court_width(self) -> float:
        """Get the court width in the configured measurement unit.

        Returns:
            `float`: Court width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._court_width_in_centimeters)

    @property
    def court_length(self) -> float:
        """Get the court length in the configured measurement unit.

        Returns:
            `float`: Court length in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._court_length_in_centimeters)

    @property
    def attack_line_distance(self) -> float:
        """Get the distance from center line to attack line.

        Returns:
            `float`: Attack line distance in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._attack_line_distance_in_centimeters
        )

    @property
    def service_area_width(self) -> float:
        """Get the service area width in the configured measurement unit.

        Returns:
            `float`: Service area width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._service_area_width_in_centimeters
        )

    @property
    def service_area_depth(self) -> float:
        """Get the service area depth in the configured measurement unit.

        Returns:
            `float`: Service area depth in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._service_area_depth_in_centimeters
        )

    @property
    def net_height(self) -> float:
        """Get the net height in the configured measurement unit.

        Returns:
            `float`: Net height in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._net_height_in_centimeters)

    @property
    def net_width(self) -> float:
        """Get the net width in the configured measurement unit.

        Returns:
            `float`: Net width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._net_width_in_centimeters)

    @property
    def center_line_width(self) -> float:
        """Get the center line width in the configured measurement unit.

        Returns:
            `float`: Center line width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._center_line_width_in_centimeters
        )

    @property
    def sideline_width(self) -> float:
        """Get the sideline width in the configured measurement unit.

        Returns:
            `float`: Sideline width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(self._sideline_width_in_centimeters)

    @property
    def attack_line_width(self) -> float:
        """Get the attack line width in the configured measurement unit.

        Returns:
            `float`: Attack line width in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._attack_line_width_in_centimeters
        )

    @property
    def service_line_distance(self) -> float:
        """Get the service line distance from baseline.

        Returns:
            `float`: Service line distance in centimeters or feet based on
                `measurement_unit` setting.
        """
        return self._to_output_unit_rounded_up(
            self._service_line_distance_in_centimeters
        )

    # internals for geometry in centimeters
    def _raw_vertices_centimeters(self) -> List[Tuple[int, int]]:
        court_width = self._court_width_in_centimeters
        court_length = self._court_length_in_centimeters
        half_length = court_length // 2
        attack_distance = self._attack_line_distance_in_centimeters
        service_depth = self._service_area_depth_in_centimeters

        return [
            # Court corners - bottom-left in RENDERED image is now (0,0)
            (0, court_width),  # 0: bottom-left corner (in rendered image)
            (0, 0),  # 1: top-left corner (in rendered image)
            (court_length, court_width),  # 2: bottom-right corner (in rendered image)
            (court_length, 0),  # 3: top-right corner (in rendered image)

            # Center line points
            (half_length, court_width),  # 4: center bottom (in rendered image)
            (half_length, 0),  # 5: center top (in rendered image)

            # Left attack line
            (half_length - attack_distance, court_width),  # 6: left attack line bottom (in rendered image)
            (half_length - attack_distance, 0),  # 7: left attack line top (in rendered image)

            # Right attack line
            (half_length + attack_distance, court_width),  # 8: right attack line bottom (in rendered image)
            (half_length + attack_distance, 0),  # 9: right attack line top (in rendered image)

            # Service area corners (left side)
            (-service_depth, court_width),  # 10: left service area bottom-left (in rendered image)
            (-service_depth, 0),  # 11: left service area top-left (in rendered image)

            # Service area corners (right side)
            (court_length + service_depth, court_width),  # 12: right service area bottom-right (in rendered image)
            (court_length + service_depth, 0),  # 13: right service area top-right (in rendered image)

            # Net position (conceptual points for drawing)
            (half_length, (3 * court_width) // 4),  # 14: net bottom quarter (in rendered image)
            (half_length, court_width // 4),  # 15: net top quarter (in rendered image)
        ]

    def _vertices_in_unit(self) -> List[Tuple[float, float]]:
        return [
            (
                self._to_output_unit_rounded_up(x),
                self._to_output_unit_rounded_up(y),
            )
            for x, y in self._raw_vertices_centimeters()
        ]

    @property
    def vertices(self) -> List[Tuple[float, float]]:
        """Get all court vertices in the configured measurement unit.
        Returns a list of coordinate pairs representing key points on the
        volleyball court for geometry calculations and visualization.

        Returns:
            `List[Tuple[float, float]]`: List of (x, y) coordinate pairs
                in centimeters or feet based on `measurement_unit` setting.
        """
        return self._vertices_in_unit()

    edges: List[Tuple[int, int]] = field(default_factory=lambda: [
        # Court perimeter
        (0, 1), (1, 3), (3, 2), (2, 0),
        # Center line
        (4, 5),
        # Left attack line
        (6, 7),
        # Right attack line
        (8, 9),
        # Service area boundaries (left)
        (10, 11),
        # Service area boundaries (right)
        (12, 13),
    ])

    labels: List[str] = field(default_factory=lambda: [
        "BL", "TL", "BR", "TR", "CB", "CT", "LAB", "LAT", "RAB", "RAT",
        "LSB", "LST", "RSB", "RST", "NB", "NT"
    ])

    colors: List[str] = field(default_factory=lambda: [
        "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FFFFFF", "#FF0000", "#FF0000",
        "#0000FF", "#0000FF", "#0000FF", "#0000FF", "#00FF00", "#00FF00",
        "#00FF00", "#00FF00", "#FFD700", "#FFD700"
    ])

    # direct index getters
    @property
    def left_court_indexes(self) -> List[int]:
        """Get vertex indexes defining the left half of the court.
        Returns the indexes into the vertices list that form the
        left side playing area.

        Returns:
            `List[int]`: List of vertex indexes forming left court polygon
                in order for drawing operations.
        """
        return [0, 1, 5, 4]

    @property
    def right_court_indexes(self) -> List[int]:
        """Get vertex indexes defining the right half of the court.
        Returns the indexes into the vertices list that form the
        right side playing area.

        Returns:
            `List[int]`: List of vertex indexes forming right court polygon
                in order for drawing operations.
        """
        return [4, 5, 3, 2]

    @property
    def left_attack_zone_indexes(self) -> List[int]:
        """Get vertex indexes defining the left attack zone.
        Returns the indexes into the vertices list that form the
        left attack zone area.

        Returns:
            `List[int]`: List of vertex indexes forming left attack zone polygon
                in order for drawing operations.
        """
        return [6, 7, 5, 4]

    @property
    def right_attack_zone_indexes(self) -> List[int]:
        """Get vertex indexes defining the right attack zone.
        Returns the indexes into the vertices list that form the
        right attack zone area.

        Returns:
            `List[int]`: List of vertex indexes forming right attack zone polygon
                in order for drawing operations.
        """
        return [4, 5, 9, 8]

    @property
    def net_center_index(self) -> int:
        """Get vertex index for the net center position.
        Returns the index into the vertices list that represents the
        center point of the net.

        Returns:
            `int`: Vertex index for net center coordinates.
        """
        return 4  # Center line bottom point represents net position

    @property
    def court_corner_indexes(self) -> List[int]:
        """Get vertex indexes for the four court corners.
        Returns the indexes into the vertices list that represent the
        four corner points of the rectangular court boundary.

        Returns:
            `List[int]`: List of vertex indexes for court corners in order:
                bottom-left, top-left, top-right, bottom-right.
        """
        return [0, 1, 3, 2]