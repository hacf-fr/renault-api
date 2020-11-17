"""Models for Renault API."""
import marshmallow


class BaseSchema(marshmallow.Schema):
    """Base schema for Gigya models to exclude unknown fields."""

    class Meta:
        """Force unknown fields to 'exclude'."""

        unknown = marshmallow.EXCLUDE
