from functools import wraps
from typing import Optional, Type, Union, get_args, get_origin
from datetime import datetime
from enum import Enum
from dataclasses import fields
import aiohttp
from config.logger_config import logger

def handle_api_response(response_type: Optional[Type] = None):
    """
    Décorateur pour analyser les réponses API et convertir en dataclass
    avec prise en charge des énumérations et datetime.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Optional[Union[dict, object]]:
            response = await func(*args, **kwargs)

            # Vérifier les statuts HTTP
            if response.status in {200, 201}:
                if response.content_type == "application/json":
                    json_data = await response.json()

                    if response_type:
                        # Gérer les listes
                        if get_origin(response_type) is list:
                            item_type = get_args(response_type)[0]
                            return [convert_to_dataclass(item, item_type) for item in json_data]

                        # Gérer un seul objet
                        return convert_to_dataclass(json_data, response_type)

                    return json_data
                return None  # Pas de contenu JSON

            elif response.status == 204:
                return None  # Pas de contenu

            # Traiter les erreurs API
            else:
                try:
                    error_data = await response.json()
                except aiohttp.ContentTypeError:
                    error_data = {"message": await response.text()}
                error_message = error_data.get("message", "Erreur non spécifiée par l'API")
                logger.error(f"Erreur API {response.status}: {error_message}")
                raise Exception(f"Erreur API {response.status}: {error_message}")

        return wrapper
    return decorator


def convert_to_dataclass(data: dict, cls: Type) -> object:
    """
    Convertit un dictionnaire en instance de dataclass, en gérant
    les champs Enum, datetime, et autres types complexes.
    """
    if not hasattr(cls, "__dataclass_fields__"):
        raise ValueError(f"{cls} n'est pas une dataclass.")

    init_args = {}
    for field in fields(cls):
        field_name = field.name
        field_type = field.type
        value = data.get(field_name)
        if value is not None:
            # Gérer les enums
            if isinstance(field_type, type) and issubclass(field_type, Enum):
                value = field_type(value)

            # Gérer datetime
            elif (field_type == datetime or field_type == Optional[datetime] and isinstance(value, str)):
                value = datetime.fromisoformat(value)

        init_args[field_name] = value

    return cls(**init_args)