from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from models import Genero, Manga  # Importamos tus modelos

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- CONEXIÓN BASE DE DATOS ---
sqlite_file_name = "mangas.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Evento: Al iniciar la app, crea las tablas si no existen
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- RUTA 1: CREAR DATOS DE PRUEBA (Para ahorrar tiempo) ---
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        # Creamos géneros
        g_shonen = Genero(nombre="Shonen")
        g_seinen = Genero(nombre="Seinen")
        session.add(g_shonen)
        session.add(g_seinen)
        session.commit() # Guardamos para tener IDs
        
        # Creamos mangas
        m1 = Manga(titulo="Naruto", autor="Kishimoto", portada_url="https://bit.ly/3Xy", genero_id=g_shonen.id)
        m2 = Manga(titulo="Berserk", autor="Miura", portada_url="https://bit.ly/3Xz", genero_id=g_seinen.id)
        session.add(m1)
        session.add(m2)
        session.commit()
    return {"mensaje": "Datos creados con éxito"}

# --- RUTA 2: EL BUSCADOR (Lo que pide el examen) ---
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = Query(None)):
    with Session(engine) as session:
        # Consulta base: Traer todo
        statement = select(Manga)
        
        # LÓGICA DEL BUSCADOR:
        if buscar:
            # Filtra si el título contiene el texto (insensible a mayúsculas)
            statement = statement.where(Manga.titulo.contains(buscar))
            
        mangas = session.exec(statement).all()
        
    return templates.TemplateResponse("mangas.html", {
        "request": request, 
        "mangas": mangas,
        "busqueda_actual": buscar # Para que el texto no se borre del input
    })

# --- RUTA 3: DASHBOARD / REPORTE ---
@app.get("/reporte")
def ver_reporte():
    with Session(engine) as session:
        total_mangas = len(session.exec(select(Manga)).all())
        total_generos = len(session.exec(select(Genero)).all())
    return {"Total Mangas": total_mangas, "Total Géneros": total_generos}