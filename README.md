# Proyecto Integrador: Colección de Mangas 📚

## Descripción
Aplicación web desarrollada con **FastAPI** y **SQLModel** para gestionar una biblioteca de Mangas. Permite buscar títulos, ver portadas y clasificar por género.

## Diagrama de Modelos
Relación: **Género (1) ----> (N) Mangas**
- Un Género tiene muchos Mangas.
- Cada Manga tiene título, autor y portada (Multimedia).

## Cómo probarlo
1. Clonar el repositorio.
2. Instalar dependencias: `pip install -r requirements.txt`
3. Ejecutar: `uvicorn main:app --reload`
4. Ir a `/mangas` para ver el dashboard.
5. `https://biblioteca-manga.onrender.com/mangas`

## Tecnologías
- Python (FastAPI)
- Jinja2 (Frontend)
- Bootstrap (Estilos)
- SQLite (Base de Datos)
