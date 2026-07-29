from sqlalchemy import create_engine

DATABASE_URL = (
    "postgresql+psycopg://energy_user:"
    "energy_password@localhost:5432/energy_dw"
)

engine = create_engine(DATABASE_URL)