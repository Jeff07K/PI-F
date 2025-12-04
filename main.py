from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
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

# --- SISTEMA DE LOGIN (NUEVO) ---
@app.post("/registro")
def registrar(request: Request, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = Usuario(username=username, password=password)
        session.add(user)
        session.commit()
    return RedirectResponse(url="/mangas", status_code=303)

@app.post("/login")
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        user = session.exec(select(Usuario).where(Usuario.username == username, Usuario.password == password)).first()
        if user:
            # Guardamos el usuario en una cookie (forma rápida para el examen)
            response = RedirectResponse(url="/mangas", status_code=303)
            response.set_cookie(key="usuario_id", value=str(user.id))
            return response
    return RedirectResponse(url="/mangas", status_code=303)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/mangas", status_code=303)
    response.delete_cookie("usuario_id")
    return response

# --- COMENTARIOS (NUEVO) ---
@app.post("/comentar/{manga_id}")
def comentar(manga_id: int, texto: str = Form(...), usuario_id: Optional[str] = Cookie(None)):
    if not usuario_id:
        return RedirectResponse(url="/mangas", status_code=303)
    
    with Session(engine) as session:
        nuevo_comentario = Comentario(texto=texto, manga_id=manga_id, usuario_id=int(usuario_id))
        session.add(nuevo_comentario)
        session.commit()
    return RedirectResponse(url="/mangas", status_code=303)

# --- RUTA PRINCIPAL (Buscador mejorado) ---
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = None, genero_id: int = None, usuario_id: Optional[str] = Cookie(None)):
    with Session(engine) as session:
        query = select(Manga)
        if buscar:
            query = query.where(Manga.titulo.contains(buscar))
        if genero_id and genero_id != 0:
            query = query.where(Manga.genero_id == genero_id)
            
        mangas = session.exec(query).all()
        generos = session.exec(select(Genero)).all()
        
        # Verificar si hay usuario logueado
        usuario_actual = None
        if usuario_id:
            usuario_actual = session.get(Usuario, int(usuario_id))

    return templates.TemplateResponse("mangas.html", {
        "request": request, 
        "mangas": mangas, 
        "generos": generos,
        "usuario": usuario_actual,
        "busqueda_actual": buscar
    })

# --- DATOS CON IMÁGENES ARREGLADAS ---
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        if session.exec(select(Genero)).first(): return {"mensaje": "Ya existen datos"}
        
        # 1. Géneros
        nombres = ["Shonen", "Seinen", "Shojo", "Terror", "Deportes"]
        gens = {}
        for n in nombres:
            g = Genero(nombre=n)
            session.add(g)
            session.commit()
            gens[n] = g.id
            
        # 2. Mangas (Links directos JPG para que no fallen)
        lista = [
            {"t": "Naruto", "a": "Kishimoto", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/81I5D0j0+BL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "One Piece", "a": "Oda", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/912xRMMRa4L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Berserk", "a": "Miura", "g": "Seinen", "img": "https://m.media-amazon.com/images/I/81M4u+-WwlL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Monster", "a": "Urasawa", "g": "Terror", "img": "https://m.media-amazon.com/images/I/8125DiM8z-L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Sailor Moon", "a": "Takeuchi", "g": "Shojo", "img": "https://m.media-amazon.com/images/I/81h4G2q-sTL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Slam Dunk", "a": "Inoue", "g": "Deportes", "img": "https://m.media-amazon.com/images/I/8166xA2tJXL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Dragon Ball", "a": "Toriyama", "g": "Shonen", "img": "https://m.media-amazon.com/images/I/81Fj80j1x+L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Akira", "a": "Otomo", "g": "Seinen", "img": "https://m.media-amazon.com/images/I/818+2q7F+5L._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Uzumaki", "a": "Junji Ito", "g": "Terror", "img": "https://m.media-amazon.com/images/I/91Ar-16-NcL._AC_UF1000,1000_QL80_.jpg"},
            {"t": "Nana", "a": "Yazawa", "g": "Shojo", "img": "https://m.media-amazon.com/images/I/61F2Kx+jXhL._AC_UF1000,1000_QL80_.jpg"}
        ]

        for i in lista:
            m = Manga(titulo=i["t"], autor=i["a"], genero_id=gens[i["g"]], portada_url=i["img"])
            session.add(m)
        
        session.commit()
    return {"mensaje": "Datos Listos"}