from typing import Dict

import reverse_geocode

from backend.common.utils.logger import logger


class CoordinatesUtil:
    @staticmethod
    def get_country_by_coordinates(latitude: str, longitude: str) -> str:
        try:
            location: Dict[str, str] = reverse_geocode.get((latitude, longitude))
            country: str = location.get("country")
            logger.info(f"Country recognized by coordinates: {country}")
            return country
        except Exception as e:
            logger.error(f"Error occurred while getting country by coordinates: {e}")
            return "Unknown Country"
