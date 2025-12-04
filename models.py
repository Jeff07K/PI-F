from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 1. Tabla Padre: GÉNERO
class Genero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    
    # Relación: Un género tiene muchos mangas
    mangas: List["Manga"] = Relationship(back_populates="genero")

# 2. Tabla Hijo: MANGA
class Manga(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    portada_url: str  # Aquí pegas el link de la imagen
    
    # Llave foránea: A qué género pertenece
    genero_id: Optional[int] = Field(default=None, foreign_key="genero.id")
    
    # Relación inversa
    genero: Optional[Genero] = Relationship(back_populates="mangas")