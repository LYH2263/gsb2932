from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import crud, models, schemas
from .auth import get_current_user, get_current_user_optional
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/community", tags=["community"])

@router.get("/posts", response_model=List[schemas.Post])
def get_posts(skip: int = 0, limit: int = 20, sort_by: str = "latest", search: Optional[str] = None, category: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_posts(db, skip=skip, limit=limit, sort_by=sort_by, search=search, category=category)

@router.get("/posts/{post_id}", response_model=schemas.Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    db_post = crud.get_post(db, post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

@router.post("/posts")
def create_post(
    post: schemas.PostCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    created_post = crud.create_post(db, post, current_user.id)
    newly_unlocked = crud.check_and_unlock_achievement(db, current_user.id, "posts_count", mark_notified=True)
    return {
        **schemas.Post.from_orm(created_post).dict(),
        "new_achievements": [schemas.Achievement.from_orm(a).dict() for a in newly_unlocked]
    }

@router.get("/posts/{post_id}/comments", response_model=List[schemas.Comment])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    return crud.get_comments(db, post_id)

@router.get("/posts/{post_id}/comments/tree", response_model=List[schemas.CommentTree])
def get_comments_tree(post_id: int, max_depth: int = 3, db: Session = Depends(get_db)):
    return crud.get_comments_tree(db, post_id, max_depth=max_depth)

@router.post("/posts/{post_id}/comments", response_model=schemas.CommentWithAuthor)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if comment.parent_id is not None:
        parent_comment = db.query(models.Comment).filter(
            models.Comment.id == comment.parent_id,
            models.Comment.post_id == post_id
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    return crud.create_comment(db, comment, post_id, current_user.id)

@router.get("/challenges", response_model=List[schemas.Challenge])
def get_challenges(db: Session = Depends(get_db)):
    return crud.get_challenges(db)

@router.get("/challenges/{challenge_id}", response_model=schemas.ChallengeDetail)
def get_challenge_detail(
    challenge_id: int,
    current_user: Optional[models.User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    challenge = crud.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    user_id = current_user.id if current_user else None
    submissions = crud.get_challenge_submissions(db, challenge_id, user_id)
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "difficulty": challenge.difficulty,
        "reward": challenge.reward,
        "start_at": challenge.start_at,
        "end_at": challenge.end_at,
        "created_at": challenge.created_at,
        "submissions": submissions
    }

@router.post("/challenges/{challenge_id}/submissions")
def create_challenge_submission(
    challenge_id: int,
    submission: schemas.ChallengeSubmissionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    challenge = crud.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    db_submission = crud.create_challenge_submission(db, current_user.id, challenge_id, submission)
    
    newly_unlocked = crud.check_and_unlock_achievement(db, current_user.id, "challenge_submissions", mark_notified=True)
    
    return {
        "id": db_submission.id,
        "title": db_submission.title,
        "description": db_submission.description,
        "link": db_submission.link,
        "user_id": db_submission.user_id,
        "challenge_id": db_submission.challenge_id,
        "score": db_submission.score,
        "vote_count": db_submission.vote_count,
        "created_at": db_submission.created_at,
        "author_name": current_user.username,
        "author_avatar": current_user.avatar,
        "user_vote": None,
        "new_achievements": [schemas.Achievement.from_orm(a).dict() for a in newly_unlocked]
    }

@router.post("/submissions/{submission_id}/vote", response_model=schemas.SubmissionVoteResponse)
def vote_submission(
    submission_id: int,
    vote_data: schemas.SubmissionVoteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result, success = crud.create_submission_vote(db, current_user.id, submission_id, vote_data.score)
    if not success:
        submission = crud.get_challenge_submission(db, submission_id)
        if submission and submission.user_id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot vote for your own submission")
        raise HTTPException(status_code=400, detail="Vote failed: already voted or invalid score")
    return result

@router.get("/challenges/{challenge_id}/leaderboard", response_model=schemas.LeaderboardResponse)
def get_challenge_leaderboard(
    challenge_id: int,
    current_user: Optional[models.User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    challenge = crud.get_challenge(db, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    user_id = current_user.id if current_user else None
    entries = crud.get_challenge_leaderboard(db, challenge_id, user_id)
    return {"entries": entries}

@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post, is_liked = crud.toggle_post_like(db, current_user.id, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if is_liked and post.author_id != current_user.id:
        crud.check_and_unlock_achievement(db, post.author_id, "likes_received")
    
    return {
        "id": post.id,
        "likes_count": post.likes_count,
        "is_liked": is_liked
    }

@router.post("/comments/{comment_id}/like")
def like_comment(
    comment_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment, is_liked = crud.toggle_comment_like(db, current_user.id, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if is_liked and comment.author_id != current_user.id:
        crud.check_and_unlock_achievement(db, comment.author_id, "likes_received")
    
    return {
        "id": comment.id,
        "likes_count": comment.likes_count,
        "is_liked": is_liked
    }

@router.get("/likes/status", response_model=schemas.LikeStatusResponse)
def get_like_status(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_likes(db, current_user.id)

@router.post("/upload/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user)
):
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的图片格式")
    
    max_size = 5 * 1024 * 1024
    content = await file.read()
    file_size = len(content)
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="图片大小不能超过 5MB")
    
    uploads_dir = Path(__file__).parent.parent / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = uploads_dir / unique_filename
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    image_url = f"/uploads/{unique_filename}"
    return {"url": image_url}
