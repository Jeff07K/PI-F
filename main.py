from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# 1. USUARIO
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    comentarios: List["Comentario"] = Relationship(back_populates="usuario")

# 2. GÉNERO
class Genero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    mangas: List["Manga"] = Relationship(back_populates="genero")

# 3. MANGA
class Manga(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    portada_url: str
    genero_id: Optional[int] = Field(default=None, foreign_key="genero.id")
    genero: Optional[Genero] = Relationship(back_populates="mangas")
    comentarios: List["Comentario"] = Relationship(back_populates="manga")

# 4. COMENTARIO
class Comentario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    texto: str
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional[Usuario] = Relationship(back_populates="comentarios")
    manga_id: Optional[int] = Field(default=None, foreign_key="manga.id")
    manga: Optional[Manga] = Relationship(back_populates="comentarios")