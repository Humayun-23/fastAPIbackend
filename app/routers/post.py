from sqlalchemy import func
from .. import models,schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import Optional,List
from sqlalchemy.orm import Session
from ..database import get_db



router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)
@router.get("/", response_model=List[schemas.PostOut])
def get_post(db: Session = Depends(get_db), limit: int= 10, skip: int=0, search: Optional[str]=""):

    posts=db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results=db.query(models.Post,func.count(
        models.Vote.post_id).label("votes")).join(
            models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(
                models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_posts(post: schemas.PostCreate,db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):

    new_post=models.Post(owner_id=current_user.id, **post.model_dump ())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostBase)
def get_posts(id: int, response: Response, db: Session = Depends(get_db)):
   
    post=db.query(models.Post).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return post

@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    updated_post=db.query(models.Post).filter(models.Post.id==id)
    up_post=updated_post.first()
    if not up_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    updated_post.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return {"data": updated_post.first()}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int= Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post=db.query(models.Post).filter(models.Post.id==id)
    post=deleted_post.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return {"data": deleted_post.first()}  