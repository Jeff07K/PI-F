from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 1. Tabla Padre: GÉNERO
class Genero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    mangas: List["Manga"] = Relationship(back_populates="genero")

# 2. Tabla Hijo: MANGA
class Manga(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    portada_url: str
    genero_id: Optional[int] = Field(default=None, foreign_key="genero.id")
    genero: Optional[Genero] = Relationship(back_populates="mangas")