from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Session, create_engine, select
from models import Genero, Manga  # Asegúrate de que models.py tenga las clases

app = FastAPI()
templates = Jinja2Templates(directory="templates")

sqlite_file_name = "mangas.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}")

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- RUTA PARA CREAR 10 MANGAS DE GOLPE ---
@app.post("/crear-datos-dummy")
def crear_datos():
    with Session(engine) as session:
        # 1. Asegurar que existan los géneros
        nombres_generos = ["Shonen", "Seinen", "Shojo", "Terror"]
        mapa_generos = {} # Diccionario para guardar los IDs

        for nombre in nombres_generos:
            genero = session.exec(select(Genero).where(Genero.nombre == nombre)).first()
            if not genero:
                genero = Genero(nombre=nombre)
                session.add(genero)
                session.commit()
                session.refresh(genero)
            mapa_generos[nombre] = genero.id

        # 2. Lista de Mangas para agregar (Títulos y Portadas Reales)
        lista_mangas = [
            {"titulo": "One Piece", "autor": "Eiichiro Oda", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/9/90/One_Piece%2C_Volume_61_Cover_%28Japanese%29.jpg"},
            {"titulo": "Dragon Ball Z", "autor": "Akira Toriyama", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/0/04/Dragon_Ball_Z_manga_vol_1.jpg"},
            {"titulo": "Attack on Titan", "autor": "Hajime Isayama", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/d/d6/Shingeki_no_Kyojin_manga_volume_1.jpg"},
            {"titulo": "Demon Slayer", "autor": "Koyoharu Gotouge", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/6/69/Kimetsu_no_Yaiba_1.png"},
            {"titulo": "Death Note", "autor": "Tsugumi Ohba", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/6/6f/Death_Note_Vol_1.jpg"},
            {"titulo": "Fullmetal Alchemist", "autor": "Hiromu Arakawa", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/9/9d/Fullmetal_Alchemist_vol_01_en.jpg"},
            {"titulo": "Tokyo Ghoul", "autor": "Sui Ishida", "genero": "Seinen", "img": "https://upload.wikimedia.org/wikipedia/en/e/e5/Tokyo_Ghoul_volume_1_cover.jpg"},
            {"titulo": "Chainsaw Man", "autor": "Tatsuki Fujimoto", "genero": "Shonen", "img": "https://upload.wikimedia.org/wikipedia/en/d/d3/Chainsaw_Man_vol._1.jpg"},
            {"titulo": "Sailor Moon", "autor": "Naoko Takeuchi", "genero": "Shojo", "img": "https://upload.wikimedia.org/wikipedia/en/0/06/Sailor_Moon_Volume_1_Kanzeban_Cover.jpg"},
            {"titulo": "Uzumaki", "autor": "Junji Ito", "genero": "Terror", "img": "https://upload.wikimedia.org/wikipedia/en/thumb/9/90/Uzumaki_manga_cover.jpg/220px-Uzumaki_manga_cover.jpg"}
        ]

        # 3. Insertar solo si no existen
        for item in lista_mangas:
            existe = session.exec(select(Manga).where(Manga.titulo == item["titulo"])).first()
            if not existe:
                nuevo_manga = Manga(
                    titulo=item["titulo"],
                    autor=item["autor"],
                    portada_url=item["img"],
                    genero_id=mapa_generos[item["genero"]]
                )
                session.add(nuevo_manga)
        
        session.commit()
    
    return {"mensaje": "¡10 Mangas agregados con éxito!"}
# RUTA DEL BUSCADOR Y LISTADO
@app.get("/mangas", response_class=HTMLResponse)
def listar_mangas(request: Request, buscar: str = Query(None)):
    with Session(engine) as session:
        query = select(Manga)
        if buscar:
            query = query.where(Manga.titulo.contains(buscar))
        mangas = session.exec(query).all()
    return templates.TemplateResponse("mangas.html", {"request": request, "mangas": mangas, "busqueda_actual": buscar})