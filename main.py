from contrib import InitLogger
from core.db import init_db, marco_engine

if __name__ == "__main__":
    InitLogger()
    init_db(marco_engine)
