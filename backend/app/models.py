from sqlalchemy import Table, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import metadata

books_table = Table(
    'books',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('file_name', String(255), nullable=False),
    Column('status', String(50), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('storage_path', String(500), nullable=True),
)

chunks_table = Table(
    'chunks',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', UUID(as_uuid=True), ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
    Column('content', Text, nullable=False),
    Column('page_number', Integer, nullable=False),
    Column('chunk_index', Integer, nullable=False),
    Column('embedding', Text, nullable=True),
    Column('created_at', DateTime, nullable=False),
)