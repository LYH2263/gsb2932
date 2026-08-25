from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import crud, schemas, models
from database import get_db
from .auth import get_current_user, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/courses", tags=["courses"])

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)

async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
):
    if token is None:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        return None
    return user

@router.get("/enrolled", response_model=List[schemas.Enrollment])
def read_enrolled_courses(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_user_enrollments(db, user_id=current_user.id)

@router.get("/", response_model=List[schemas.Course])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses

@router.get("/recommended", response_model=schemas.RecommendedCourseResponse)
async def get_recommended(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional)
):
    user_id = current_user.id if current_user else None
    
    courses, reason_course, reason_tags, is_personalized = crud.get_recommended_courses(
        db, user_id=user_id, limit=limit
    )
    
    return {
        "courses": courses,
        "reason_course": reason_course,
        "reason_tags": reason_tags,
        "is_personalized": is_personalized
    }

@router.get("/trending", response_model=List[schemas.CourseWithNewEnrollments])
def get_trending(
    days: int = 7,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return crud.get_trending_courses(db, days=days, limit=limit)

@router.get("/{course_id}", response_model=schemas.Course)
def read_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course

@router.post("/{course_id}/enroll", response_model=schemas.Enrollment)
def enroll_course(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    existing_enrollment = crud.get_enrollment(db, user_id=current_user.id, course_id=course_id)
    if existing_enrollment:
        raise HTTPException(status_code=400, detail="Already enrolled")
        
    return crud.create_enrollment(db=db, user_id=current_user.id, course_id=course_id)

@router.put("/{course_id}/progress", response_model=schemas.Enrollment)
def update_progress(course_id: int, enrollment_update: schemas.EnrollmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing_enrollment = crud.get_enrollment(db, user_id=current_user.id, course_id=course_id)
    if not existing_enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    
    return crud.update_enrollment_progress(
        db=db,
        user_id=current_user.id,
        course_id=course_id,
        progress=enrollment_update.progress,
        last_lesson_id=enrollment_update.last_lesson_id
    )

class PurchaseRequest(BaseModel):
    coupon_code: Optional[str] = None

@router.post("/{course_id}/purchase", response_model=schemas.Order)
def purchase_course(
    course_id: int,
    request: Optional[PurchaseRequest] = Body(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    course = crud.get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if course.is_free:
        raise HTTPException(status_code=400, detail="Cannot purchase a free course")

    existing_orders = crud.get_user_orders(db, current_user.id)
    for order in existing_orders:
        if order.course_id == course_id and order.status == "completed":
             pass

    coupon_code = request.coupon_code if request and request.coupon_code else None
    price_info = crud.calculate_final_price(db, course_id, coupon_code, current_user.id)
    if not price_info:
        raise HTTPException(status_code=404, detail="Course not found")
    
    if coupon_code and price_info["coupon"]:
        crud.mark_user_coupon_used(db, current_user.id, price_info["coupon"].id)

    order_data = schemas.OrderCreate(
        total_amount=price_info["final_price"],
        course_id=course.id,
        status="completed"
    )
    
    order = crud.create_order(db=db, order=order_data, user_id=current_user.id)
    
    existing_enrollment = crud.get_enrollment(db, user_id=current_user.id, course_id=course_id)
    if not existing_enrollment:
        crud.create_enrollment(db=db, user_id=current_user.id, course_id=course_id)
        
    return order

@router.get("/{course_id}/reviews", response_model=List[schemas.ReviewDetail])
def get_reviews(course_id: int, db: Session = Depends(get_db)):
    return crud.get_course_reviews(db, course_id)

@router.post("/{course_id}/reviews", response_model=schemas.ReviewDetail)
def create_review(course_id: int, review: schemas.ReviewCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if review.course_id != course_id:
        raise HTTPException(status_code=400, detail="Course mismatch")
    created = crud.create_review(db, current_user.id, review)
    return {
        "id": created.id,
        "rating": created.rating,
        "content": created.content,
        "course_id": created.course_id,
        "user_id": created.user_id,
        "created_at": created.created_at,
        "username": current_user.username,
        "avatar": current_user.avatar
    }

@router.get("/{course_id}/questions", response_model=List[schemas.QuestionDetail])
def get_questions(course_id: int, db: Session = Depends(get_db)):
    return crud.get_course_questions(db, course_id)

@router.post("/{course_id}/questions", response_model=schemas.QuestionDetail)
def create_question(course_id: int, question: schemas.QuestionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if question.course_id != course_id:
        raise HTTPException(status_code=400, detail="Course mismatch")
    created = crud.create_question(db, current_user.id, question)
    return {
        "id": created.id,
        "title": created.title,
        "content": created.content,
        "course_id": created.course_id,
        "user_id": created.user_id,
        "views": created.views,
        "created_at": created.created_at,
        "author_name": current_user.username,
        "author_avatar": current_user.avatar,
        "comments_count": 0,
        "answers": []
    }

@router.post("/{course_id}/lessons/{lesson_id}/complete")
def mark_lesson_complete_api(course_id: int, lesson_id: int, body: schemas.LessonProgressMarkComplete, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    enrollment = crud.get_enrollment(db, current_user.id, course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    lesson = db.query(models.Lesson).filter(models.Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lp, created = crud.mark_lesson_complete(db, current_user.id, lesson_id, body.study_duration)
    if not created:
        return {
            **schemas.LessonProgress.from_orm(lp).dict(),
            "already_completed": True,
            "message": "该课时已完成，无需重复标记",
            "new_achievements": []
        }
    
    user = crud.get_user(db, current_user.id)
    if user:
        today = datetime.utcnow().date()
        if user.last_study_date:
            last_date = user.last_study_date.date()
            if last_date != today:
                if (today - last_date).days == 1:
                    user.consecutive_days += 1
                elif (today - last_date).days > 1:
                    user.consecutive_days = 1
        else:
            user.consecutive_days = 1
        user.last_study_date = datetime.utcnow()
        user.total_study_time += body.study_duration
        db.commit()
    
    crud.sync_enrollment_progress(db, current_user.id, course_id)
    
    newly_unlocked = []
    newly_unlocked += crud.check_and_unlock_achievement(db, current_user.id, "study_hours", mark_notified=True)
    newly_unlocked += crud.check_and_unlock_achievement(db, current_user.id, "completed_courses", mark_notified=True)
    newly_unlocked += crud.check_and_unlock_achievement(db, current_user.id, "consecutive_days", mark_notified=True)
    newly_unlocked += crud.check_and_unlock_achievement(db, current_user.id, "all_free_courses", mark_notified=True)
    
    return {
        **schemas.LessonProgress.from_orm(lp).dict(),
        "already_completed": False,
        "new_achievements": [schemas.Achievement.from_orm(a).dict() for a in newly_unlocked]
    }

@router.get("/{course_id}/progress", response_model=schemas.CourseProgressResponse)
def get_course_progress(course_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    enrollment = crud.get_enrollment(db, current_user.id, course_id)
    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    progress = crud.get_course_lesson_progress(db, current_user.id, course_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Course not found")
    return progress
