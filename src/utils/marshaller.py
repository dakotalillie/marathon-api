from flask_restful import fields


class Marshaller:
    def __init__(self, fields_dict):
        self.__fields = fields_dict

    def all(self):
        return self.__fields

    def pick(self, *properties):
        return {k: v for k, v in self.__fields.items() if k in properties}

    def omit(self, *properties):
        return {k: v for k, v in self.__fields.items() if k not in properties}


class CommonMarshaller(Marshaller):
    def __init__(self, fields_dict):
        super().__init__(
            {
                **fields_dict,
                "id": fields.String,
                "created_at": fields.DateTime(dt_format="iso8601"),
                "updated_at": fields.DateTime(dt_format="iso8601"),
                "is_active": fields.Boolean,
            }
        )
