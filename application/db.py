from sqlalchemy import MetaData, create_engine

metadata = MetaData()


def create_db_engine(config):
    """Creates database engine"""
    engine = create_engine(
        f"postgresql://{config['PG_USER']}:{config['PG_PASS']}"
        f"@{config['PG_HOST']}:{config['PG_PORT']}/{config['PG_NAME']}",
        echo=config["PG_ECHO"],
    )
    return engine
