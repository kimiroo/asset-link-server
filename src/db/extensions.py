"""
SQLAlchemy compiler extensions for PostgreSQL Row-Level Security (RLS).

Provides native Python constructs to handle 'SET LOCAL', 'ENABLE RLS', and 'CREATE POLICY'
statements, eliminating raw SQL strings from the application layer to maintain strict type safety.
"""

from typing import Any

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.expression import Executable, ClauseElement
from sqlalchemy.schema import DDLElement

class SetLocal(Executable, ClauseElement):
    inherit_cache: bool | None = False

    parameter: str
    value: Any

    def __init__(self, parameter: str, value: Any) -> None:
        self.parameter = parameter
        self.value = value

@compiles(SetLocal, "postgresql")
def compile_set_local(element: SetLocal, compiler: SQLCompiler, **kw: Any) -> str:
    """Compile the SET LOCAL parameter statement for PostgreSQL."""
    compiled_value: str = compiler.process(element.value, **kw)
    return f"SET LOCAL {element.parameter} = {compiled_value}"


class EnableRLS(DDLElement):
    inherit_cache: bool | None = False
    table: Any

    def __init__(self, table: Any) -> None:
        self.table = table

@compiles(EnableRLS, "postgresql")
def compile_enable_rls(element: EnableRLS, compiler: SQLCompiler, **kw: Any) -> str:
    """Compile the ALTER TABLE ENABLE ROW LEVEL SECURITY statement."""
    table_name: str = compiler.process(element.table, include_schema=False)
    return f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"


class CreatePolicy(DDLElement):
    inherit_cache: bool | None = False
    name: str
    table: Any
    criterion: ClauseElement

    def __init__(self, name: str, table: Any, criterion: ClauseElement) -> None:
        self.name = name
        self.table = table
        self.criterion = criterion

@compiles(CreatePolicy, "postgresql")
def compile_create_policy(element: CreatePolicy, compiler: SQLCompiler, **kw: Any) -> str:
    """Compile the CREATE POLICY statement using SQLAlchemy criteria."""
    table_name: str = compiler.process(element.table, include_schema=False)
    criterion_sql: str = compiler.process(element.criterion, **kw)
    return f"CREATE POLICY {element.name} ON {table_name} USING ({criterion_sql})"
