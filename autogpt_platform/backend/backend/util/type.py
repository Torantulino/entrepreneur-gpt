import json
from typing import Any, Type, TypeVar, cast, get_args, get_origin

from prisma import Json as PrismaJson


class ConversionError(ValueError):
    pass


def __convert_list(value: Any) -> list:
    if isinstance(value, (list, tuple, set)):
        return list(value)
    elif isinstance(value, dict):
        return list(value.items())
    elif isinstance(value, str):
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [value]
        else:
            return [value]
    else:
        return [value]


def __convert_dict(value: Any) -> dict:
    if isinstance(value, str):
        try:
            result = json.loads(value)
            if isinstance(result, dict):
                return result
            else:
                return {"value": result}
        except json.JSONDecodeError:
            return {"value": value}  # Fallback conversion
    elif isinstance(value, list):
        return {i: value[i] for i in range(len(value))}
    elif isinstance(value, tuple):
        return {i: value[i] for i in range(len(value))}
    elif isinstance(value, dict):
        return value
    else:
        return {"value": value}


def __convert_tuple(value: Any) -> tuple:
    if isinstance(value, (str, list, set)):
        return tuple(value)
    elif isinstance(value, dict):
        return tuple(value.items())
    elif isinstance(value, (int, float, bool)):
        return (value,)
    elif isinstance(value, tuple):
        return value
    else:
        return (value,)


def __convert_set(value: Any) -> set:
    if isinstance(value, (str, list, tuple)):
        return set(value)
    elif isinstance(value, dict):
        return set(value.items())
    elif isinstance(value, set):
        return value
    else:
        return {value}


def __convert_str(value: Any) -> str:
    if isinstance(value, str):
        return value
    else:
        return json.dumps(value)


NUM = TypeVar("NUM", int, float)


def __convert_num(value: Any, num_type: Type[NUM]) -> NUM:
    if isinstance(value, (list, dict, tuple, set)):
        return num_type(len(value))
    elif isinstance(value, num_type):
        return value
    else:
        try:
            return num_type(float(value))
        except (ValueError, TypeError):
            return num_type(0)  # Fallback conversion


def __convert_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        if value.lower() in ["true", "1"]:
            return True
        else:
            return False
    else:
        return bool(value)


def _try_convert(value: Any, target_type: Type, raise_on_mismatch: bool) -> Any:
    origin = get_origin(target_type)
    args = get_args(target_type)
    if origin is None:
        origin = target_type
    if origin not in [list, dict, tuple, str, set, int, float, bool]:
        return value

    # Handle the case when value is already of the target type
    if isinstance(value, origin):
        if not args:
            return value
        else:
            # Need to convert elements
            if origin is list:
                return [convert(v, args[0]) for v in value]
            elif origin is tuple:
                # Tuples can have multiple types
                if len(args) == 1:
                    return tuple(convert(v, args[0]) for v in value)
                else:
                    return tuple(convert(v, t) for v, t in zip(value, args))
            elif origin is dict:
                key_type, val_type = args
                return {
                    convert(k, key_type): convert(v, val_type) for k, v in value.items()
                }
            elif origin is set:
                return {convert(v, args[0]) for v in value}
            else:
                return value
    elif raise_on_mismatch:
        raise TypeError(f"Value {value} is not of expected type {target_type}")
    else:
        # Need to convert value to the origin type
        if origin is list:
            value = __convert_list(value)
            if args:
                return [convert(v, args[0]) for v in value]
            else:
                return value
        elif origin is dict:
            value = __convert_dict(value)
            if args:
                key_type, val_type = args
                return {
                    convert(k, key_type): convert(v, val_type) for k, v in value.items()
                }
            else:
                return value
        elif origin is tuple:
            value = __convert_tuple(value)
            if args:
                if len(args) == 1:
                    return tuple(convert(v, args[0]) for v in value)
                else:
                    return tuple(convert(v, t) for v, t in zip(value, args))
            else:
                return value
        elif origin is str:
            return __convert_str(value)
        elif origin is set:
            value = __convert_set(value)
            if args:
                return {convert(v, args[0]) for v in value}
            else:
                return value
        elif origin is int:
            return __convert_num(value, int)
        elif origin is float:
            return __convert_num(value, float)
        elif origin is bool:
            return __convert_bool(value)
        else:
            return value


T = TypeVar("T")


def type_match(value: Any, target_type: Type[T]) -> T:
    return cast(T, _try_convert(value, target_type, raise_on_mismatch=True))


def convert(value: Any, target_type: Type[T]) -> T:
    try:
        if isinstance(value, PrismaJson):
            value = value.data
        return cast(T, _try_convert(value, target_type, raise_on_mismatch=False))
    except Exception as e:
        raise ConversionError(f"Failed to convert {value} to {target_type}") from e
