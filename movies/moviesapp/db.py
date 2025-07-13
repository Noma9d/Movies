from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import os
from datetime import datetime
from configparser import ConfigParser


config = ConfigParser()
config.read("condfig.ini")
# Read database configuration from the config file
db_file = config.get("DB", "db_file", fallback="db.sqlite3")
db_connection_string = config.get("DB", "db_connection_string", fallback="sqlite:///db.sqlite3")

Base = declarative_base()

# Create the database engine
engine = create_engine(db_connection_string, echo=False)
Session = sessionmaker(bind=engine)
session = Session()

# Association tables
record_tags = Table(
    "record_tags",
    Base.metadata,
    Column("record_id", Integer, ForeignKey("records.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)

record_actors = Table(
    "record_actors",
    Base.metadata,
    Column("record_id", Integer, ForeignKey("records.id")),
    Column("actor_id", Integer, ForeignKey("actors.id")),
)


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(String)
    release_date = Column(Date)
    genre = Column(String(50))
    extension = Column(String(10))
    size = Column(Integer)
    download_url = Column(String(200))
    created_at = Column(Date, default=datetime.now)

    tags = relationship("Tag", secondary="record_tags")
    picture_id = Column(Integer, ForeignKey("pictures.id"))
    picture = relationship("Picture", backref="records")
    actors = relationship("Actor", secondary="record_actors")

    def __init__(
        self,
        title,
        description,
        release_date,
        genre,
        extension,
        size,
        download_url,
        picture_id=None,
        actors=None,
        tags=None,
    ):
        self.title = title
        self.description = description
        # Преобразуем строку даты в объект datetime.date
        if isinstance(release_date, str):
            self.release_date = datetime.strptime(release_date, "%Y-%m-%d").date()
        else:
            self.release_date = release_date
        self.genre = genre
        self.extension = extension
        self.size = size
        self.download_url = download_url
        self.picture_id = picture_id
        self.actors = actors if actors else []
        self.tags = tags if tags else []

    def save(self):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, record_id):
        return session.query(cls).filter_by(id=record_id).first()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        return self

    def delete(self):
        session.delete(self)
        session.commit()


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def save(self):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_name(cls, name):
        return session.query(cls).filter_by(name=name).first()

    @classmethod
    def get_by_id(cls, tag_id):
        return session.query(cls).filter_by(id=tag_id).first()

    def update(self, name):
        self.name = name
        session.commit()
        return self

    def delete(self):
        session.delete(self)
        session.commit()


class Actor(Base):
    __tablename__ = "actors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)
    bio = Column(String)
    image_path = Column(String(200))

    def __init__(self, name, age, bio, image_path):
        self.name = name
        self.age = age
        self.bio = bio
        self.image_path = image_path

    def save(self):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, actor_id):
        return session.query(cls).filter_by(id=actor_id).first()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        return self

    def delete(self):
        session.delete(self)
        session.commit()


class Picture(Base):
    __tablename__ = "pictures"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # Имя файла
    image_path = Column(String(200))  # Путь к файлу

    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

    def save(self):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def get_by_path(cls, path):
        return session.query(cls).filter_by(image_path=path).first()

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, id):
        return session.query(cls).filter_by(id=id).first()

    def delete(self):
        session.delete(self)
        session.commit()

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, picture_id):
        return session.query(cls).filter_by(id=picture_id).first()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        return self

    def delete(self):
        session.delete(self)
        session.commit()

    def save(self):
        session.add(self)
        session.commit()
        return self

    @classmethod
    def get_all(cls):
        return session.query(cls).all()

    @classmethod
    def get_by_id(cls, picture_id):
        return session.query(cls).filter_by(id=picture_id).first()

    def update(self, name=None, image=None):
        if name:
            self.name = name
        if image:
            self.image_path = image
        session.commit()
        return self

    def delete(self):
        session.delete(self)
        session.commit()


# Create tables if they don't exist
Base.metadata.create_all(engine)

# Helper functions for file uploads
UPLOAD_FOLDER = "static/uploads"


def save_file(file, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    filename = secure_filename(file.filename)
    filepath = os.path.join(folder, filename)
    file.save(filepath)
    return filepath


def delete_file(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

        # Association tables (moved to the top of the file)
        self.description = description
