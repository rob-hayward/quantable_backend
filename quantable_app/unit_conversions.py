# quantable_app/unit_conversions.py

from .enums import Category, SizeUnit, VolumeUnit, WeightUnit, LengthUnit, AreaUnit, TemperatureUnit, TimeUnit, \
    SpeedUnit, NumberUnit, CurrencyUnit


def convert_size(value, from_unit, to_unit):
    if from_unit == SizeUnit.CENTIMETER.value and to_unit == SizeUnit.METER.value:
        return value / 100
    elif from_unit == SizeUnit.METER.value and to_unit == SizeUnit.CENTIMETER.value:
        return value * 100
    elif from_unit == SizeUnit.INCH.value and to_unit == SizeUnit.CENTIMETER.value:
        return value * 2.54
    elif from_unit == SizeUnit.CENTIMETER.value and to_unit == SizeUnit.INCH.value:
        return value / 2.54
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_volume(value, from_unit, to_unit):
    if from_unit == VolumeUnit.MILLILITER.value and to_unit == VolumeUnit.LITER.value:
        return value / 1000
    elif from_unit == VolumeUnit.LITER.value and to_unit == VolumeUnit.MILLILITER.value:
        return value * 1000
    elif from_unit == VolumeUnit.CUBIC_CENTIMETER.value and to_unit == VolumeUnit.MILLILITER.value:
        return value
    elif from_unit == VolumeUnit.MILLILITER.value and to_unit == VolumeUnit.CUBIC_CENTIMETER.value:
        return value
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_weight(value, from_unit, to_unit):
    if from_unit == WeightUnit.GRAM.value and to_unit == WeightUnit.KILOGRAM.value:
        return value / 1000
    elif from_unit == WeightUnit.KILOGRAM.value and to_unit == WeightUnit.GRAM.value:
        return value * 1000
    elif from_unit == WeightUnit.OUNCE.value and to_unit == WeightUnit.GRAM.value:
        return value * 28.34952
    elif from_unit == WeightUnit.GRAM.value and to_unit == WeightUnit.OUNCE.value:
        return value / 28.34952
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_length(value, from_unit, to_unit):
    if from_unit == LengthUnit.CENTIMETER.value and to_unit == LengthUnit.METER.value:
        return value / 100
    elif from_unit == LengthUnit.METER.value and to_unit == LengthUnit.CENTIMETER.value:
        return value * 100
    elif from_unit == LengthUnit.INCH.value and to_unit == LengthUnit.CENTIMETER.value:
        return value * 2.54
    elif from_unit == LengthUnit.CENTIMETER.value and to_unit == LengthUnit.INCH.value:
        return value / 2.54
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_area(value, from_unit, to_unit):
    if from_unit == AreaUnit.SQUARE_METER.value and to_unit == AreaUnit.SQUARE_CENTIMETER.value:
        return value * 10000
    elif from_unit == AreaUnit.SQUARE_CENTIMETER.value and to_unit == AreaUnit.SQUARE_METER.value:
        return value / 10000
    elif from_unit == AreaUnit.SQUARE_FOOT.value and to_unit == AreaUnit.SQUARE_METER.value:
        return value * 0.09290304
    elif from_unit == AreaUnit.SQUARE_METER.value and to_unit == AreaUnit.SQUARE_FOOT.value:
        return value / 0.09290304
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_temperature(value, from_unit, to_unit):
    if from_unit == TemperatureUnit.CELSIUS.value and to_unit == TemperatureUnit.FAHRENHEIT.value:
        return (value * 9/5) + 32
    elif from_unit == TemperatureUnit.FAHRENHEIT.value and to_unit == TemperatureUnit.CELSIUS.value:
        return (value - 32) * 5/9
    elif from_unit == TemperatureUnit.CELSIUS.value and to_unit == TemperatureUnit.KELVIN.value:
        return value + 273.15
    elif from_unit == TemperatureUnit.KELVIN.value and to_unit == TemperatureUnit.CELSIUS.value:
        return value - 273.15
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_time(value, from_unit, to_unit):
    if from_unit == TimeUnit.SECOND.value and to_unit == TimeUnit.MINUTE.value:
        return value / 60
    elif from_unit == TimeUnit.MINUTE.value and to_unit == TimeUnit.SECOND.value:
        return value * 60
    elif from_unit == TimeUnit.HOUR.value and to_unit == TimeUnit.MINUTE.value:
        return value * 60
    elif from_unit == TimeUnit.MINUTE.value and to_unit == TimeUnit.HOUR.value:
        return value / 60
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")

def convert_speed(value, from_unit, to_unit):
    if from_unit == SpeedUnit.METERS_PER_SECOND.value and to_unit == SpeedUnit.KILOMETERS_PER_HOUR.value:
        return value * 3.6
    elif from_unit == SpeedUnit.KILOMETERS_PER_HOUR.value and to_unit == SpeedUnit.METERS_PER_SECOND.value:
        return value / 3.6
    elif from_unit == SpeedUnit.MILES_PER_HOUR.value and to_unit == SpeedUnit.KILOMETERS_PER_HOUR.value:
        return value * 1.60934
    elif from_unit == SpeedUnit.KILOMETERS_PER_HOUR.value and to_unit == SpeedUnit.MILES_PER_HOUR.value:
        return value / 1.60934
    # Add more conversion conditions as needed
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")


def convert_number(value, from_unit, to_unit):
    if from_unit == NumberUnit.WHOLE.value and to_unit == NumberUnit.DECIMAL.value:
        return float(value)
    elif from_unit == NumberUnit.DECIMAL.value and to_unit == NumberUnit.WHOLE.value:
        return int(value)
    elif from_unit == NumberUnit.PERCENTAGE.value and to_unit == NumberUnit.DECIMAL.value:
        return value / 100
    elif from_unit == NumberUnit.DECIMAL.value and to_unit == NumberUnit.PERCENTAGE.value:
        return value * 100
    else:
        raise ValueError(f"Unsupported unit conversion: {from_unit} to {to_unit}")


def convert_currency(value, from_unit, to_unit):
    # Hardcoded conversion rates for development purposes
    conversion_rates = {
        CurrencyUnit.USD.value: 1.0,
        CurrencyUnit.EUR.value: 0.92,
        CurrencyUnit.GBP.value: 0.81,
        CurrencyUnit.JPY.value: 135.0,
        CurrencyUnit.CAD.value: 1.32,
        CurrencyUnit.AUD.value: 1.47,
        CurrencyUnit.CHF.value: 0.96,
        CurrencyUnit.CNY.value: 6.80,
        CurrencyUnit.HKD.value: 7.75,
        CurrencyUnit.SGD.value: 1.37,
    }

    if from_unit not in conversion_rates or to_unit not in conversion_rates:
        raise ValueError(f"Unsupported currency units: {from_unit} to {to_unit}")

    from_rate = conversion_rates[from_unit]
    to_rate = conversion_rates[to_unit]

    converted_value = (value / from_rate) * to_rate
    return converted_value


UNIT_CONVERSION_FUNCTIONS = {
    Category.SIZE: convert_size,
    Category.VOLUME: convert_volume,
    Category.WEIGHT: convert_weight,
    Category.LENGTH: convert_length,
    Category.AREA: convert_area,
    Category.TEMPERATURE: convert_temperature,
    Category.TIME: convert_time,
    Category.SPEED: convert_speed,
    Category.NUMBER: convert_number,
    Category.CURRENCY: convert_currency,
}


