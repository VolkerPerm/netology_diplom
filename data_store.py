import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, Session, session, sessionmaker
from sqlalchemy import create_engine, MetaData
import psycopg2

from config import db_url_object

Base = declarative_base()
engine = sqlalchemy.create_engine(db_url_object)
metadata = MetaData()
Session = sessionmaker(bind=engine)
session = Session()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def add_bd(user_id, search_id):
    '''Добавление в базу данных'''
    to_bd = Viewed(profile_id=user_id, worksheet_id=search_id)
    session.add(to_bd)
    session.commit()

def extraction_bd(user_id):
    '''Извлечение из базы данных'''
    ext_bd = list()
    from_bd = session.query(Viewed).filter(Viewed.profile_id == user_id).all()
    for item in from_bd:
        ext_bd.append(item.worksheet_id)
    return ext_bd

def checked(user_id, user):
    '''Проверка есть ли в базе данных пользователь'''
    extraction_bd(user_id)
    if user in extraction_bd(user_id):
        return False
    return True



if __name__ == '__main__':
    create_tables(engine)
    print(extraction_bd(199494788))
    print(checked(199494788, 139520938))

