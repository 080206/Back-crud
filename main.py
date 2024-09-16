from typing import List

from fastapi import FastAPI, HTTPException, Depends

from pydantic import BaseModel

from sqlalchemy import Column, Integer, String, create_engine

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import sessionmaker, Session

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Adjust to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()



# Definición del modelo de base de datos

class CategoryModel(Base):

  __tablename__ = "categories"

  id = Column(Integer, primary_key=True, index=True)

  name = Column(String, index=True)



Base.metadata.create_all(bind=engine)



# Pydantic model for request and response validation

class Category(BaseModel):

  id: int

  name: str



  class Config:

    orm_mode = True



# Dependencia para obtener la sesión de la base de datos

def get_db():

  db = SessionLocal()

  try:

    yield db

  finally:

    db.close()



# Crear una categoría

@app.post("/categories/", response_model=Category)

def create_category(category: Category, db: Session = Depends(get_db)):

  db_category = CategoryModel(id=category.id, name=category.name)

  db.add(db_category)

  db.commit()

  db.refresh(db_category)

  return db_category



# Leer todas las categorías

@app.get("/categories/", response_model=List[Category])

def read_categories(db: Session = Depends(get_db)):

  return db.query(CategoryModel).all()



# Leer una categoría por ID

@app.get("/categories/{category_id}", response_model=Category)

def read_category(category_id: int, db: Session = Depends(get_db)):

  category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

  if category is None:

    raise HTTPException(status_code=404, detail="Category not found")

  return category



# Actualizar una categoría por ID

@app.put("/categories/{category_id}", response_model=Category)

def update_category(category_id: int, updated_category: Category, db: Session = Depends(get_db)):

  category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

  if category is None:

    raise HTTPException(status_code=404, detail="Category not found")

   

  category.name = updated_category.name

  db.commit()

  db.refresh(category)

  return category



# Eliminar una categoría por ID

@app.delete("/categories/{category_id}", response_model=Category)

def delete_category(category_id: int, db: Session = Depends(get_db)):

  category = db.query(CategoryModel).filter(CategoryModel.id == category_id).first()

  if category is None:

    raise HTTPException(status_code=404, detail="Category not found")

   

  db.delete(category)

  db.commit()

  return category



# Para correr la aplicación: uvicorn main:app --reload











