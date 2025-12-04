from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from models import Genero, Manga  # Asegúrate de que models.py tenga las clases que creamos

app = FastAPI()
templates = Jinja2Templates(directory="templates")

sqlite_file_name = "mangas.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# RUTA PARA CREAR DATOS DE EJEMPLO (DALE CLICK UNA VEZ)
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        if not session.exec(select(Genero)).first(): # Solo crea si está vacío
            g1 = Genero(nombre="Shonen")
            session.add(g1)
            session.commit()
            m1 = Manga(titulo="Naruto", autor="Kishimoto", portada_url="https://upload.wikimedia.org/wikipedia/en/9/94/NarutoCoverTankobon1.jpg", genero_id=g1.id)
            session.add(m1)
            session.commit()
    return {"mensaje": "Datos listos"}

# RUTA DEL BUSCADOR Y LISTADO
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = Query(None)):
    with Session(engine) as session:
        query = select(Manga)
        if buscar:
            query = query.where(Manga.titulo.contains(buscar))
        mangas = session.exec(query).all()
    return templates.TemplateResponse("mangas.html", {"request": request, "mangas": mangas, "busqueda_actual": buscar})