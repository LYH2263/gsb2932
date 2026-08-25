from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import crud, models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/dashboard")
def get_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_dashboard(db, current_user.id)

@router.get("/enrollments", response_model=list[schemas.Enrollment])
def get_enrollments(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_enrollments(db, current_user.id)

@router.get("/projects", response_model=List[schemas.UserProject])
def get_projects(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_projects(db, current_user.id)

@router.post("/projects", response_model=schemas.UserProject)
def create_project(
    project: schemas.UserProjectCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.create_user_project(db, project, current_user.id)

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.delete_user_project(db, project_id, current_user.id)
    return {"message": "Project deleted"}

@router.get("/favorites", response_model=List[schemas.Course])
def get_favorites(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_favorites(db, current_user.id)

@router.post("/favorites/{course_id}")
def add_favorite(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.add_favorite(db, current_user.id, course_id)
    return {"message": "Added to favorites"}

@router.delete("/favorites/{course_id}")
def remove_favorite(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crud.remove_favorite(db, current_user.id, course_id)
    return {"message": "Removed from favorites"}

@router.get("/orders", response_model=List[schemas.Order])
def get_orders(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_orders(db, current_user.id)

@router.get("/course-study-time/{course_id}")
def get_course_study_time(
    course_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    duration = crud.get_course_study_duration(db, current_user.id, course_id)
    return {"course_id": course_id, "study_duration": duration}

@router.get("/enrollments-with-time")
def get_enrollments_with_time(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enrollments = crud.get_user_enrollments(db, current_user.id)
    result = []
    for e in enrollments:
        study_duration = crud.get_course_study_duration(db, current_user.id, e.course_id)
        result.append({
            "user_id": e.user_id,
            "course_id": e.course_id,
            "progress": e.progress,
            "joined_at": e.joined_at,
            "last_lesson_id": e.last_lesson_id,
            "course": {
                "id": e.course.id,
                "title": e.course.title,
                "description": e.course.description,
                "level": e.course.level,
                "price": e.course.price,
                "cover_image": e.course.cover_image,
                "instructor": e.course.instructor,
                "rating": e.course.rating,
                "students_count": e.course.students_count,
                "is_free": e.course.is_free,
                "tags": e.course.tags,
                "chapters": []
            },
            "study_duration": study_duration
        })
    return result

@router.get("/achievements")
def get_user_achievements(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    achievements = crud.get_user_achievement_progress(db, current_user.id)
    
    unnotified = db.query(models.UserAchievement).filter(
        models.UserAchievement.user_id == current_user.id,
        models.UserAchievement.notified == False
    ).all()
    
    new_achievements = []
    for ua in unnotified:
        achievement = db.query(models.Achievement).filter(
            models.Achievement.id == ua.achievement_id
        ).first()
        if achievement:
            new_achievements.append(schemas.Achievement.from_orm(achievement).dict())
        ua.notified = True
    db.commit()
    
    return {
        "achievements": achievements,
        "new_achievements": new_achievements
    }
