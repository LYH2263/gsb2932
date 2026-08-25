from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
import io
import contextlib
import subprocess
import tempfile
import os
from database import get_db
import crud, models, schemas
from routers.auth import get_current_user

router = APIRouter(
    prefix="/sandbox",
    tags=["sandbox"]
)

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

@router.post("/execute")
def execute_code(request: CodeExecutionRequest):
    language = request.language.lower()
    if language == "python":
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(request.code, {"__builtins__": __builtins__}, {})
            return {"output": stdout.getvalue(), "error": None}
        except Exception as e:
            return {"output": "", "error": str(e)}
    if language == "javascript":
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as temp_file:
                temp_file.write(request.code)
                temp_path = temp_file.name
            result = subprocess.run(
                ["node", temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = (result.stdout or "").strip()
            error = (result.stderr or "").strip()
            if result.returncode != 0 and not error:
                error = "JavaScript execution failed"
            return {"output": output, "error": error or None}
        except FileNotFoundError:
            return {"output": "", "error": "Node.js is not available on the server"}
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "JavaScript execution timed out"}
        finally:
            if "temp_path" in locals() and os.path.exists(temp_path):
                os.unlink(temp_path)
    return {"output": "", "error": f"Language '{request.language}' is not supported"}

@router.post("/snippets", response_model=schemas.CodeSnippet)
def save_snippet(
    snippet: schemas.CodeSnippetCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_code_snippet(db, snippet, current_user.id)

@router.get("/snippets", response_model=List[schemas.CodeSnippet])
def get_my_snippets(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_code_snippets(db, current_user.id)

@router.patch("/snippets/{snippet_id}", response_model=schemas.CodeSnippet)
def update_snippet(
    snippet_id: int,
    snippet_update: schemas.CodeSnippetUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_snippet = crud.get_code_snippet(db, snippet_id)
    if not db_snippet or db_snippet.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Snippet not found")
    if snippet_update.title is not None:
        db_snippet.title = snippet_update.title
    if snippet_update.code is not None:
        db_snippet.code = snippet_update.code
    if snippet_update.language is not None:
        db_snippet.language = snippet_update.language
    if snippet_update.is_public is not None:
        db_snippet.is_public = snippet_update.is_public
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

@router.delete("/snippets/{snippet_id}")
def delete_snippet(
    snippet_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted = crud.delete_code_snippet(db, snippet_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return {"message": "Deleted"}

@router.get("/shared/{share_token}", response_model=schemas.SharedCodeSnippet)
def get_shared_snippet(share_token: str, db: Session = Depends(get_db)):
    snippet = crud.get_code_snippet_by_share_token(db, share_token)
    if not snippet or not snippet.is_public:
        raise HTTPException(status_code=404, detail="Snippet not found or not public")
    user = crud.get_user(db, snippet.user_id)
    return schemas.SharedCodeSnippet(
        id=snippet.id,
        title=snippet.title,
        code=snippet.code,
        language=snippet.language,
        share_token=snippet.share_token,
        created_at=snippet.created_at,
        author_name=user.username if user else "Unknown",
        author_avatar=user.avatar if user else None
    )
