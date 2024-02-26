from sqlalchemy import types, Column, Table, func
from sqlalchemy.dialects.postgresql import JSONB
from ckan.model import meta
from ckan.model import types as _types
from ckan.model.domain_object import DomainObject


# Define dbca_spatial table structure.
dbca_spatial_table = Table(
    'dbca_spatial', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column('label', types.UnicodeText, nullable=False, unique=True),
    Column('geometry', JSONB, nullable=False)
)


class DbcaSpatial(DomainObject):
    u"""
    DbcaSpatial object.
    """

    def __init__(self, label=None, geometry=None):
        self.label = label
        self.geometry = geometry

    @classmethod
    def get_by_label(cls, label):
        """
        Returns the spatial object by label.
        """
        query = meta.Session.query(cls)
        return query.filter(func.lower(cls.label) == func.lower(label)).first()

    @classmethod
    def get_like_label(cls, label, limit=None):
        """
        Returns the spatial objects that contain the label.
        """
        if limit is None:
            limit = 50
        query = meta.Session.query(cls)
        return query.filter(func.lower(cls.label).contains(func.lower(label))).order_by(cls.label).limit(limit).all()

    @classmethod
    def get_by_geometry(cls, geometry):
        """
        Returns the spatial object by geometry.
        """
        query = meta.Session.query(cls)
        return query.filter(cls.geometry == geometry).first()


meta.mapper(DbcaSpatial, dbca_spatial_table)
