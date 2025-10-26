from src.exceptions.generic_exceptions import NotFoundException

class CountryNotFoundException(NotFoundException):
    def __init__(self, country_name: str):
        super().__init__(detail=f"Country {country_name} not found")