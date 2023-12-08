from typing import Any, Dict, Optional, Union

from sqlalchemy.exc import IntegrityError, NoResultFound, OperationalError
from sqlalchemy.orm.exc import FlushError
from sqlmodel import SQLModel, select

from contrib import BaseLogging

logger = BaseLogging("model_failed_execution")


class ActiveRecordMixin:
    __config__ = None

    @property
    def primary_key(self):
        return self.__mapper__.primary_key_from_instance(self)  # type: ignore

    @classmethod
    def first(cls, session):
        statement = select(cls)
        return session.exec(statement).first()

    @classmethod
    def one_by_id(cls, session, id: int):
        obj = session.get(cls, id)
        return obj

    @classmethod
    def first_by_field(cls, session, field: str, value: Any):
        return cls.first_by_fields(session, {field: value})

    @classmethod
    def one_by_field(cls, session, field: str, value: Any):
        return cls.one_by_fields(session, {field: value})

    @classmethod
    def first_by_fields(cls, session, fields: dict):
        statement = select(cls)
        for key, value in fields.items():
            statement = statement.where(getattr(cls, key) == value)
        try:
            return session.exec(statement).first()
        except NoResultFound:
            logger.error(f"{cls}: first_by_fields failed, NoResultFound")
            return None

    @classmethod
    def one_by_fields(cls, session, fields: dict):
        statement = select(cls)
        for key, value in fields.items():
            statement = statement.where(getattr(cls, key) == value)
        try:
            return session.exec(statement).one()
        except NoResultFound:
            logger.error(f"{cls}: one_by_fields failed, NoResultFound")
            return None

    @classmethod
    def all_by_field(cls, session, field: str, value: Any):
        statement = select(cls).where(getattr(cls, field) == value)
        return session.exec(statement).all()

    @classmethod
    def all_by_fields(cls, session, fields: dict):
        statement = select(cls)
        for key, value in fields.items():
            statement = statement.where(getattr(cls, key) == value)
        return session.exec(statement).all()

    @classmethod
    def convert_without_saving(
        cls,
        source: Union[Dict[str, Any], SQLModel],
        update: Optional[Dict[str, Any]] = None,
    ) -> SQLModel:
        # try:
        if isinstance(source, SQLModel):
            obj = cls.model_validate(source, update=update)  # type: ignore
        elif isinstance(source, dict):
            obj = cls.parse_obj(source, update=update)  # type: ignore
        # except ValidationError:
        #    return None
        return obj

    @classmethod
    def create(
        cls,
        session,
        source: Union[Dict[str, Any], SQLModel],
        update: Optional[Dict[str, Any]] = None,
    ) -> Optional[SQLModel]:
        obj = cls.convert_without_saving(source, update)
        if obj is None:
            return None
        if obj.save(session):
            return obj
        return None

    @classmethod
    def create_or_update(
        cls,
        session,
        source: Union[Dict[str, Any], SQLModel],
        update: Optional[Dict[str, Any]] = None,
    ) -> Optional[SQLModel]:
        obj = cls.convert_without_saving(source, update)
        if obj is None:
            return None
        pk = cls.__mapper__.primary_key_from_instance(obj)  # type: ignore
        if pk[0] is not None:
            existing = session.get(cls, pk)
            if existing is None:
                return None  # Error
            else:
                existing.update(session, obj)  # Update
                return existing
        else:
            return cls.create(session, obj)  # Create

    @classmethod
    def count(cls, session) -> int:
        return len(cls.all(session))

    def refresh(self, session):
        session.refresh(self)

    def save(self, session) -> bool:
        session.add(self)
        try:
            session.commit()
            session.refresh(self)
            return True
        except (IntegrityError, OperationalError, FlushError) as e:
            logger.error(e)
            session.rollback()
            return False

    def update(self, session, source: Union[dict, SQLModel]):
        if isinstance(source, SQLModel):
            source = source.model_dump(exclude_unset=True)

        for key, value in source.items():
            setattr(self, key, value)
        self.save(session)

    def delete(self, session):
        session.delete(self)
        session.commit()

    @classmethod
    def all(cls, session):
        return session.exec(select(cls)).all()

    @classmethod
    def delete_all(cls, session):
        for obj in cls.all(session):
            obj.delete(session)
