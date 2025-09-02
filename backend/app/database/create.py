from settings import Base, engine


def create(table_name):

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)
    print("Table created successfully")