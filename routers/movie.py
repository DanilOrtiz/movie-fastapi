from fastapi import Path, Query, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field 
from typing import Optional
from user_jwt import validateToken
from bd.database import Session
from models.movie import Movie as ModelMovie
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter

routerMovie = APIRouter()

class BearerJWT(HTTPBearer ):
    async def __call__(self, request: Request):
        try:
            auth = await super().__call__(request)
            data = validateToken(auth.credentials)
            if data['email'] != 'test@gmail.com':
                raise HTTPException(status_code = 403, detail= 'Credenciales incorrectas')
            return auth
        except Exception as e:
            raise HTTPException(
                status_code=403, 
                detail="Credenciales inválidas"
            )
        
class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(defult= "Titulo de la pelicula" ,min_length = 5, max_length = 60)
    overview: str = Field(defult= "Descripcion de la pelicula" ,min_length = 5, max_length = 60)
    year: int = Field(default = 2023)
    rating: float = Field(ge = 1, le=10)
    category: str = Field(min_length=3,max_length=100, default="aqui la categoria")
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "overview": self.overview,
            "year": self.year,
            "rating": self.rating,
            "category": self.category
        }
    
@routerMovie.get('/movies', tags=['Movies'], dependencies=[Depends(BearerJWT())])
def get_movies():
    db = Session()
    data = db.query(ModelMovie).all()

    return JSONResponse(content=jsonable_encoder(data))

@routerMovie.get('/movies/{id}', tags=['Movies'])
def get_movie(id: int = Path(ge=1, le=100)):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data: 
        return JSONResponse(status_code=404, content={'message': 'Recurso no encontrado'})
    return JSONResponse(status_code=200, content=jsonable_encoder(data))
     
@routerMovie.get('/movies/', tags=['Movies'])
def get_movies_by_category(category: str = Query(min_length=3,max_length=15)):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.category == category).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(data))

@routerMovie.post('/movies', tags=['Movies'], status_code=201)
def create_movie(movie: Movie):
    try:
        db = Session()
        new_movie = ModelMovie(**movie.dict())
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)  # Actualizar el objeto con los datos de la BD
        return JSONResponse(
            status_code=201,
            content={
                'message': 'Se ha cargado una nueva pelicula',
                'movie': new_movie.to_dict()
            }
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@routerMovie.put('/movies/{id}', tags=['Movies'], status_code=200)
def update_movie(id: int, movie: Movie):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()

    if not data:
        return JSONResponse(status_code=404, content={'message': 'No se encontró el recurso'})
    
    data.title = movie.title
    data.overview = movie.overview
    data.year = movie.year
    data.rating = movie.rating
    data.category = movie.category
    db.commit()
    return JSONResponse(content={'message':'Se ha modificado la pelicula'})

@routerMovie.delete('/movies/{id}', tags=['Movies'], status_code=200)
def delete_movie(id: int):
    db = Session()
    data = db.query(ModelMovie).filter(ModelMovie.id == id).first()
    if not data:
        return JSONResponse(status_code=404, content={'message': 'No se encontró el recurso'})
    db.delete(data)
    db.commit()
    return JSONResponse(content={'message':'Se ha eliminado la pelicula'})



