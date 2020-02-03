"""Initialize DB."""
import click

from airflow_utils.models import Base, DB


@click.command(help="Initialize schema for PostgreSQL.")
def main():
    """Click command to initialize DB in PostgreSQL."""
    db = DB("postgres")
    Base.metadata.create_all(db.engine)
