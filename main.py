from fastapi import FastAPI, Request, Form, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from typing import Optional
from models import Genero, Manga, Usuario, Comentario

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- CONEXIÓN DB ---
sqlite_file_name = "mangas.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- USUARIOS (LOGIN/REGISTRO) ---
@app.post("/registro")
def registrar(username: str = Form(...), password: str = Form(...)):
    with Session(engine) as session:
        # Verificar si existe
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

# --- LISTA Y BUSCADOR (CORREGIDO EL ERROR DETACHED) ---
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = None, genero_id: int = 0, usuario_id: Optional[str] = Cookie(None)):
    with Session(engine) as session:
        query = select(Manga)
        if buscar: 
            query = query.where(Manga.titulo.contains(buscar))
        if genero_id and genero_id != 0: 
            query = query.where(Manga.genero_id == genero_id)
            
        mangas = session.exec(query).all()
        generos = session.exec(select(Genero)).all()
        
        usuario_actual = None
        if usuario_id:
            usuario_actual = session.get(Usuario, int(usuario_id))

        # ESTA ES LA GARANTÍA: El return está DENTRO del "with"
        return templates.TemplateResponse("mangas.html", {
            "request": request, 
            "mangas": mangas, 
            "generos": generos,
            "usuario": usuario_actual,
            "busqueda_actual": buscar
        })

# --- GENERADOR DE DATOS CON IMÁGENES HD ESTABLES (WIKIPEDIA) ---
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        # Verificar si ya existen datos para no repetir
        if session.exec(select(Genero)).first(): 
            return {"mensaje": "¡Los datos ya existen! Borra mangas.db si quieres recargar."}
        
        # 1. Crear Géneros
        nombres_generos = ["Shonen", "Seinen", "Shojo", "Terror", "Deportes"]
        mapa_generos = {}
        
        for nombre in nombres_generos:
            g = Genero(nombre=nombre)
            session.add(g)
            session.commit()
            session.refresh(g)
            mapa_generos[nombre] = g.id
            
        # 2. Crear Mangas (Links de Wikipedia que NO caducan)
        lista_mangas = [
            {
                "t": "Naruto", 
                "a": "Masashi Kishimoto", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/9/94/NarutoCoverTankobon1.jpg"
            },
            {
                "t": "One Piece", 
                "a": "Eiichiro Oda", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/9/90/One_Piece%2C_Volume_61_Cover_%28Japanese%29.jpg"
            },
            {
                "t": "Dragon Ball", 
                "a": "Akira Toriyama", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/c/c9/DB_Vol_1_cover.jpg"
            },
            {
                "t": "Attack on Titan", 
                "a": "Hajime Isayama", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/d/d6/Shingeki_no_Kyojin_manga_volume_1.jpg"
            },
            {
                "t": "Fullmetal Alchemist", 
                "a": "Hiromu Arakawa", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/9/9d/Fullmetal_Alchemist_vol_01_en.jpg"
            },
            {
                "t": "Death Note", 
                "a": "Tsugumi Ohba", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/6/6f/Death_Note_Vol_1.jpg"
            },
            {
                "t": "Demon Slayer", 
                "a": "Koyoharu Gotouge", 
                "g": "Shonen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/6/69/Kimetsu_no_Yaiba_1.png"
            },
            {
                "t": "Sailor Moon", 
                "a": "Naoko Takeuchi", 
                "g": "Shojo", 
                "img": "https://upload.wikimedia.org/wikipedia/en/0/06/Sailor_Moon_Volume_1_Kanzeban_Cover.jpg"
            },
            {
                "t": "Tokyo Ghoul", 
                "a": "Sui Ishida", 
                "g": "Seinen", 
                "img": "https://upload.wikimedia.org/wikipedia/en/e/e5/Tokyo_Ghoul_volume_1_cover.jpg"
            },
            {
                "t": "Uzumaki", 
                "a": "Junji Ito", 
                "g": "Terror", 
                "img": "https://upload.wikimedia.org/wikipedia/en/thumb/9/90/Uzumaki_manga_cover.jpg/220px-Uzumaki_manga_cover.jpg"
            }
        ]

        for item in lista_mangas:
            nuevo_manga = Manga(
                titulo=item["t"],
                autor=item["a"],
                portada_url=item["img"],
                genero_id=mapa_generos[item["g"]]
            )
            session.add(nuevo_manga)
        
        session.commit()
        
    return {"mensaje": "¡10 Mangas creados con imágenes HD exitosamente!"}
    with Session(engine) as session:
        if session.exec(select(Genero)).first(): return {"mensaje": "Datos ya existen"}
        
        # Generos
        nombres = ["Shonen", "Seinen", "Shojo", "Terror", "Deportes"]
        mapa = {}
        for n in nombres:
            g = Genero(nombre=n)
            session.add(g)
            session.commit()
            mapa[n] = g.id
            
        # Mangas
        datos = [
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

        for d in datos:
            session.add(Manga(titulo=d["t"], autor=d["a"], genero_id=mapa[d["g"]], portada_url=d["img"]))
        session.commit()
    return {"mensaje": "Datos creados"}