"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

# TODO: Implement your FastAPI app here

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from typing import List
from src import models, database, schemas
from .database import engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=database.engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        active_nodes = db.query(models.Node).filter(models.Node.status == "active").count()
        return {"status": "ok", "db": "connected", "nodes_count": active_nodes}
    except Exception:
        return {"status": "error", "db": "disconnected", "nodes_count": 0}
    
@app.post("/api/nodes", response_model=schemas.NodeResponse, status_code=status.HTTP_201_CREATED)
def create_node(node: schemas.NodeCreate, db: Session = Depends(get_db)):
    db_node = models.Node(**node.model_dump())
    try:
        db.add(db_node)
        db.commit()
        db.refresh(db_node)
        return db_node
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Node name already exists"
        )

@app.get("/api/nodes", response_model=list[schemas.NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(models.Node).all()

@app.get("/api/nodes", response_model=List[schemas.NodeResponse])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(models.Node).all()


@app.get("/api/nodes/{name}", response_model=schemas.NodeResponse)
def get_node(name: str, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@app.put("/api/nodes/{name}", response_model=schemas.NodeResponse)
def update_node(name: str, node_update: schemas.NodeUpdate, db: Session = Depends(database.get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if node_update.host is not None:
        node.host = node_update.host
    if node_update.port is not None:
        node.port = node_update.port
    db.commit()
    db.refresh(node)
    return node

@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(get_db)):
    node = db.query(models.Node).filter(models.Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = "inactive"
    db.commit()