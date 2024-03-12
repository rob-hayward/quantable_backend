# quantable_app/enums.py

from enum import Enum

class Category(Enum):
    SIZE = 'size'
    VOLUME = 'volume'
    WEIGHT = 'weight'
    CURRENCY = 'currency'
    LENGTH = 'length'
    AREA = 'area'
    TEMPERATURE = 'temperature'
    TIME = 'time'
    SPEED = 'speed'
    NUMBER = 'number'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class SizeUnit(Enum):
    CENTIMETER = 'cm'
    METER = 'm'
    INCH = 'inch'
    FOOT = 'ft'
    YARD = 'yd'
    MILE = 'mi'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class VolumeUnit(Enum):
    MILLILITER = 'ml'
    LITER = 'l'
    CUBIC_CENTIMETER = 'cm³'
    CUBIC_METER = 'm³'
    TEASPOON = 'tsp'
    TABLESPOON = 'tbsp'
    FLUID_OUNCE = 'fl oz'
    CUP = 'cup'
    PINT = 'pt'
    QUART = 'qt'
    GALLON = 'gal'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class WeightUnit(Enum):
    MILLIGRAM = 'mg'
    GRAM = 'g'
    KILOGRAM = 'kg'
    OUNCE = 'oz'
    POUND = 'lb'
    TON = 'ton'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class CurrencyUnit(Enum):
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    JPY = 'JPY'
    CAD = 'CAD'
    AUD = 'AUD'
    CHF = 'CHF'
    CNY = 'CNY'
    HKD = 'HKD'
    SGD = 'SGD'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class LengthUnit(Enum):
    MILLIMETER = 'mm'
    CENTIMETER = 'cm'
    METER = 'm'
    KILOMETER = 'km'
    INCH = 'inch'
    FOOT = 'ft'
    YARD = 'yd'
    MILE = 'mi'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class AreaUnit(Enum):
    SQUARE_MILLIMETER = 'mm²'
    SQUARE_CENTIMETER = 'cm²'
    SQUARE_METER = 'm²'
    SQUARE_KILOMETER = 'km²'
    SQUARE_INCH = 'in²'
    SQUARE_FOOT = 'ft²'
    SQUARE_YARD = 'yd²'
    SQUARE_MILE = 'mi²'
    ACRE = 'acre'
    HECTARE = 'ha'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class TemperatureUnit(Enum):
    CELSIUS = '°C'
    FAHRENHEIT = '°F'
    KELVIN = 'K'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class TimeUnit(Enum):
    MILLISECOND = 'ms'
    SECOND = 's'
    MINUTE = 'min'
    HOUR = 'h'
    DAY = 'd'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class SpeedUnit(Enum):
    METERS_PER_SECOND = 'm/s'
    KILOMETERS_PER_HOUR = 'km/h'
    MILES_PER_HOUR = 'mph'
    KNOTS = 'knots'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class NumberUnit(Enum):
    WHOLE = 'whole'
    DECIMAL = 'decimal'
    PERCENTAGE = 'percentage'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


CATEGORY_UNIT_MAPPING = {
    Category.SIZE: SizeUnit,
    Category.VOLUME: VolumeUnit,
    Category.WEIGHT: WeightUnit,
    Category.CURRENCY: CurrencyUnit,
    Category.LENGTH: LengthUnit,
    Category.AREA: AreaUnit,
    Category.TEMPERATURE: TemperatureUnit,
    Category.TIME: TimeUnit,
    Category.SPEED: SpeedUnit,
    Category.NUMBER: NumberUnit,
}