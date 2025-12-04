from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Optional
from models import Genero, Manga, Usuario, Comentario

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- CONEXIÓN BASE DE DATOS ---
sqlite_file_name = "mangas.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- LOGIN Y REGISTRO ---
@app.post("/registro")
def registrar(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        if not session.exec(select(Usuario).where(Usuario.username == username)).first():
            user = Usuario(username=username, password=password)
            session.add(user)
            session.commit()
    return RedirectResponse(url="/mangas", status_code=303)

@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.username == username, Usuario.password == password)).first()
        if user:
            response = RedirectResponse(url="/mangas", status_code=303)
            response.set_cookie(key="usuario_id", value=str(user.id))
            return response
    return RedirectResponse(url="/mangas", status_code=303)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/mangas", status_code=303)
    response.delete_cookie("usuario_id")
    return response

# --- COMENTARIOS ---
@app.post("/comentar/{manga_id}")
def comentar(manga_id: int, texto: str = Form(...), usuario_id: Optional[str] = Cookie(None)):
    if usuario_id:
        with Session(engine) as session:
            c = Comentario(texto=texto, manga_id=manga_id, usuario_id=int(usuario_id))
            session.add(c)
            session.commit()
    return RedirectResponse(url="/mangas", status_code=303)

# --- LISTA Y BUSCADOR ---
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = None, genero_id: int = 0, usuario_id: Optional[str] = Cookie(None)):
    with Session(engine) as session:
        query = select(Manga)
        if buscar: query = query.where(Manga.titulo.contains(buscar))
        if genero_id and genero_id != 0: query = query.where(Manga.genero_id == genero_id)
        
        mangas = session.exec(query).all()
        generos = session.exec(select(Genero)).all()
        usuario = session.get(Usuario, int(usuario_id)) if usuario_id else None

    return templates.TemplateResponse("mangas.html", {
        "request": request, "mangas": mangas, "generos": generos, 
        "usuario": usuario, "busqueda_actual": buscar
    })

# --- DATOS DE PRUEBA ---
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        if session.exec(select(Genero)).first(): return {"mensaje": "Datos ya existen"}
        
        # Crear Géneros
        nombres = ["Shonen", "Seinen", "Shojo", "Terror"]
        mapa = {}
        for n in nombres:
            g = Genero(nombre=n)
            session.add(g)
            session.commit()
            mapa[n] = g.id
            
        # Crear Mangas
        datos = [
            {"t": "Naruto", "a": "Kishimoto", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/81I5D0j0+BL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "One Piece", "a": "Oda", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/912xRMMRa4L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Berserk", "a": "Miura", "g": "Seinen", "img": "https://m.media-amazon.com/images/I/81M4u+-WwlL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Dragon Ball", "a": "Toriyama", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/81Fj80j1x+L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Uzumaki", "a": "Junji Ito", "g": "Terror", "img": "https://m.media-amazon.com/images/I/91Ar-16-NcL._AC_UF1000,1000_QL80_.jpg"}
        ]
        for d in datos:
            session.add(Manga(titulo=d["t"], autor=d["a"], genero_id=mapa[d["g"]], portada_url=d["img"]))
        session.commit()
    return {"mensaje": "Datos creados"}