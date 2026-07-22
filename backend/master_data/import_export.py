import csv
import io
from typing import Any

from .models import (
    Airline,
    Airport,
    CabinClass,
    City,
    Country,
    Currency,
    FareType,
    Language,
    PassengerType,
    StateRegion,
    TripType,
)


class ImportExportService:
    model_map = {
        "countries": Country,
        "states": StateRegion,
        "cities": City,
        "airports": Airport,
        "airlines": Airline,
        "currencies": Currency,
        "languages": Language,
        "cabin-classes": CabinClass,
        "passenger-types": PassengerType,
        "trip-types": TripType,
        "fare-types": FareType,
    }

    fields_config = {
        "countries": ["id", "code", "name"],
        "states": ["id", "country_id", "code", "name"],
        "cities": ["id", "state_id", "code", "name"],
        "airports": ["id", "city_id", "code", "name"],
        "airlines": ["id", "code", "name"],
        "currencies": ["id", "code", "name", "symbol"],
        "languages": ["id", "code", "name"],
        "cabin-classes": ["id", "code", "name"],
        "passenger-types": ["id", "code", "name"],
        "trip-types": ["id", "code", "name"],
        "fare-types": ["id", "code", "name"],
    }

    @classmethod
    def export_csv(cls, model_name: str) -> str:
        if model_name not in cls.model_map:
            raise KeyError(f"Invalid model name: {model_name}")
        model = cls.model_map[model_name]
        queryset = model.objects.filter(is_deleted=False)
        field_names = cls.fields_config[model_name]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=field_names)
        writer.writeheader()
        for record in queryset:
            row = {}
            for field in field_names:
                row[field] = getattr(record, field, "")
            writer.writerow(row)
        return output.getvalue()

    @classmethod
    def import_csv(cls, model_name: str, csv_data: str) -> int:
        if model_name not in cls.model_map:
            raise KeyError(f"Invalid model name: {model_name}")
        model = cls.model_map[model_name]
        reader = csv.DictReader(io.StringIO(csv_data))
        count = 0
        for row in reader:
            lookup = {}
            if row.get("id"):
                lookup["id"] = int(row["id"])
            elif row.get("code"):
                lookup["code"] = row["code"]
            else:
                lookup["name"] = row.get("name")

            defaults = {}
            for field in cls.fields_config[model_name]:
                if field == "id":
                    continue
                if field in row:
                    val = row[field]
                    if val == "":
                        val = None
                    elif field.endswith("_id") and val is not None:
                        val = int(val)
                    defaults[field] = val

            model.objects.update_or_create(**lookup, defaults=defaults)
            count += 1
        return count
