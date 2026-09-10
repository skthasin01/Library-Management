from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres.rwsendftbzgmnghpnmxy:Li12BraryMa@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={'check_same_thread':False})

Sessionlocal = sessionmaker(autoflush=False,autocommit=False,bind=engine)

Base = declarative_base()