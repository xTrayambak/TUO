import json
import gzip
import enum
import copy

class SerializationType(enum.Enum):
    STRING = 0
    BYTES = 1
    COMPRESSED_BYTES = 2


def is_attr_ready_only(obj: object, attr: str) -> bool:
    """
    A really hacky way of determining if any attribute is read-only.
    """
    if attr in NO_ALTER_ATTRS: return True
    original_value = getattr(obj, attr)

    try:
        setattr(obj, attr, None)
        return False
    except AttributeError as exc:
        if 'read-only' or 'not writable' in exc.args[0]:
            return True
        else:
            return False


    setattr(obj, attr, original_value)

NO_ALTER_ATTRS = (
    '__class__'
)


class PatchedDict:
    def __init__(self, obj: dict):
        self.type = "dict"
        self.keys = obj

class PatchedList:
    def __init__(self, obj: list):
        self.type = "list"
        self.items = obj

class Serializer:
    """
    Data serializer/deserializer.
    """
    def __init__(self, compression_level: int = 4):
        self.compression_level = compression_level


    def serialize(self, data: object, serialization_type = SerializationType.STRING) -> str | bytes:
        """
        Serialize an object.
        """
        disected_data = self.disect(data)

        if serialization_type == SerializationType.BYTES: return disected_data.encode('utf-8')
        elif serialization_type == SerializationType.COMPRESSED_BYTES:
            return gzip.compress(
                disected_data.encode('utf-8'),
                self.compression_level
            )
        elif serialization_type == SerializationType.STRING: return disected_data


    def disect(self, obj: object) -> str:
        """
        Format an object to be JSON-encodable (i.e disect it).
        """
        obj = copy.copy(obj)
        attributes = []

        if isinstance(obj, dict):
            obj = PatchedDict(obj)

        if isinstance(obj, list):
            obj = PatchedList(obj)

        for attr_name in obj.__dir__():
            if attr_name.startswith('__'): continue
            attr_value = getattr(obj, attr_name)

            # Screw 'em functions.
            if callable(attr_value):
                if not is_attr_ready_only(obj, attr_name) and attr_name not in NO_ALTER_ATTRS:
                    setattr(obj, attr_name, None)

        return json.dumps(obj.__dict__, indent=4)


    def deserialize(self, stream: bytes, serialization_type: SerializationType = SerializationType.STRING) -> object:
        """
        Deserialize a stream of bytes back to a Python dictionary.
        """
        if serialization_type == SerializationType.COMPRESSED_BYTES:
            stream = gzip.decompress(stream)
        elif serialization_type == SerializationType.BYTES:
            stream = stream.decode('utf-8')

        json_data = json.loads(stream)

        if 'type' in json_data:
            if json_data['type'] == 'dict' and 'keys' in json_data:
                json_data = json_data['keys']
            elif json_data['type'] == 'list' and 'items' in json_data:
                json_data = json_data['items']

        return json_data
