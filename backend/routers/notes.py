from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import crud, models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("", response_model=List[schemas.Note])
def get_notes(
    course_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    search: Optional[str] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_notes(db, current_user.id, course_id, lesson_id, search)

@router.get("/{note_id}", response_model=schemas.Note)
def get_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    note = crud.get_note(db, note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("", response_model=schemas.Note)
def create_note(
    note: schemas.NoteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_note(db, note, current_user.id)

@router.put("/{note_id}", response_model=schemas.Note)
def update_note(
    note_id: int,
    note_update: schemas.NoteUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    updated_note = crud.update_note(db, note_id, note_update, current_user.id)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@router.delete("/{note_id}")
def delete_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.delete_note(db, note_id, current_user.id)
    return {"message": "Note deleted"}
