from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Optional
from models import Genero, Manga, Usuario, Comentario

app = FastAPI()
templates = Jinja2Templates(directory="templates")

sqlite_file_name = "mangas.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.post("/registro")
def registrar(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        if not session.exec(select(Usuario).where(Usuario.username == username)).first():
            session.add(Usuario(username=username, password=password))
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

@app.post("/comentar/{manga_id}")
def comentar(manga_id: int, texto: str = Form(...), usuario_id: Optional[str] = Cookie(None)):
    if usuario_id:
        with Session(engine) as session:
            session.add(Comentario(texto=texto, manga_id=manga_id, usuario_id=int(usuario_id)))
            session.commit()
    return RedirectResponse(url="/mangas", status_code=303)

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

@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        if session.exec(select(Genero)).first(): return {"mensaje": "Datos listos"}
        nombres = ["Shonen", "Seinen", "Shojo", "Terror"]
        mapa = {}
        for n in nombres:
            g = Genero(nombre=n)
            session.add(g)
            session.commit()
            mapa[n] = g.id

        # IMAGENES DE WIKIPEDIA (NO FALLAN)
        datos = [
            {"t": "Naruto", "a": "Kishimoto", "g": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/9/94/NarutoCoverTankobon1.jpg"},
            {"t": "One Piece", "a": "Oda", "g": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/9/90/One_Piece%2C_Volume_61_Cover_%28Japanese%29.jpg"},
            {"t": "Dragon Ball", "a": "Toriyama", "g": "Shonen", "img": "https://i.pinimg.com/736x/e2/07/2a/e2072a5a25e2e12cd9e2629d18464194.jpg"},
            {"t": "Sailor Moon", "a": "Takeuchi", "g": "Shojo", "img": "https://i.pinimg.com/1200x/c6/81/5d/c6815d9f6b1e7fefedb1d29d5e48e580.jpg"},
            {"t": "Uzumaki", "a": "Junji Ito", "g": "Terror", "img": "https://i.pinimg.com/736x/28/53/9e/28539eb00611994ff252b03573c1ec51.jpg"}
        ]
        for d in datos:
            session.add(Manga(titulo=d["t"], autor=d["a"], genero_id=mapa[d["g"]], portada_url=d["img"]))
        session.commit()
    return {"mensaje": "Datos Creados"}