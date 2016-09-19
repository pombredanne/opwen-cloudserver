from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from opwen_cloudserver.state import AccountsStore
from opwen_cloudserver.state import DeliveredEmailsStore

_Base = declarative_base()


class _Account(_Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True)
    client = Column(String(64), nullable=False, index=True)
    user = Column(String(256), nullable=False, index=True)
    email = Column(String(256), nullable=False, index=True, unique=True)


class _DeliveredEmail(_Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    client = Column(String(64), nullable=False, index=True)
    email_hash = Column(Integer, nullable=False, index=True, unique=True)


class _BaseSqlStore(object):
    def __init__(self, database_uri):
        """
        :type database_uri: str

        """
        engine = create_engine(database_uri)
        _Base.metadata.create_all(engine)
        _Base.metadata.bind = engine
        create_session = sessionmaker(bind=engine)
        self._engine = engine
        self._session = create_session()


class SqlAccountsStore(AccountsStore, _BaseSqlStore):
    def __init__(self, database_uri, email_host):
        """
        :type database_uri: str
        :type email_host: str

        """
        _BaseSqlStore.__init__(self, database_uri)
        self._email_host = email_host

    def get(self, client_name, email_or_username):
        client = client_name.lower()
        user = email_or_username.lower()

        account = self._session.query(_Account).filter(and_(
            _Account.client == client,
            _Account.user == user,
        )).first()

        if account is not None:
            return account.email

        if '@' in email_or_username:
            return email_or_username

        raise ValueError

    def create(self, client_name, username):
        email = self._format_email(
            client=client_name,
            user=username,
            host=self._email_host)

        self._session.add(_Account(
            client=client_name.lower(),
            user=username.lower(),
            email=email.lower()))

        try:
            self._session.commit()
        except IntegrityError:
            self._session.rollback()

        return email


class SqlDeliveredEmailsStore(DeliveredEmailsStore, _BaseSqlStore):
    def contains(self, client_name, email):
        client = client_name.lower()
        email_hash = self._hash_email(email)

        return self._session.query(_DeliveredEmail).filter(and_(
            _DeliveredEmail.client == client,
            _DeliveredEmail.email_hash == email_hash,
        )).first() is not None

    def delete(self, client_name):
        client = client_name.lower()

        self._session.query(_DeliveredEmail).filter(
            _DeliveredEmail.client == client
        ).delete()

        try:
            self._session.commit()
        except DatabaseError:
            # TODO: log failure
            self._session.rollback()

    def add(self, client_name, email):
        client = client_name.lower()
        email_hash = self._hash_email(email)

        self._session.add(_DeliveredEmail(
            client=client,
            email_hash=email_hash,
        ))

        try:
            self._session.commit()
        except DatabaseError:
            self._session.rollback()
            return False
        else:
            return True
