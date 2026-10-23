from collections.abc import Mapping

from rest_framework import serializers


class StrictFieldsMixin:
    """Reject request fields the serializer doesn't define, so a typo like `phnoe` is an error instead of silently dropped."""

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            unknown = sorted(set(data) - set(self.fields))
            if unknown:
                raise serializers.ValidationError({name: "Unknown field." for name in unknown})
        return super().to_internal_value(data)
