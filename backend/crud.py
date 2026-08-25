from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
import models, schemas
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        avatar=user.avatar,
        bio=user.bio
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    if user_update.avatar is not None:
        db_user.avatar = user_update.avatar
    if user_update.bio is not None:
        db_user.bio = user_update.bio
    if user_update.password:
        db_user.hashed_password = get_password_hash(user_update.password)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db_user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_courses(db: Session, skip: int = 0, limit: int = 100, level=None, is_free=None, search=None):
    query = db.query(models.Course)
    if level:
        query = query.filter(models.Course.level == level)
    if is_free is not None:
        query = query.filter(models.Course.is_free == is_free)
    if search:
        query = query.filter(models.Course.title.contains(search))
    return query.offset(skip).limit(limit).all()

def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).options(joinedload(models.Course.chapters).joinedload(models.Chapter.lessons)).first()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(
        title=course.title,
        description=course.description,
        level=course.level,
        price=course.price,
        cover_image=course.cover_image,
        instructor=course.instructor,
        rating=course.rating,
        students_count=course.students_count,
        is_free=course.is_free,
        tags=course.tags
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    for chapter_data in course.chapters:
        db_chapter = models.Chapter(
            title=chapter_data.title,
            order=chapter_data.order,
            course_id=db_course.id
        )
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        
        for lesson_data in chapter_data.lessons:
            db_lesson = models.Lesson(
                title=lesson_data.title,
                type=lesson_data.type,
                content=lesson_data.content,
                video_url=lesson_data.video_url,
                duration=lesson_data.duration,
                order=lesson_data.order,
                chapter_id=db_chapter.id
            )
            db.add(db_lesson)
    
    db.commit()
    db.refresh(db_course)
    return db_course

def get_enrollment(db: Session, user_id: int, course_id: int):
    return db.query(models.Enrollment).filter(models.Enrollment.user_id == user_id, models.Enrollment.course_id == course_id).first()

def create_enrollment(db: Session, user_id: int, course_id: int):
    db_enrollment = models.Enrollment(user_id=user_id, course_id=course_id)
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment

def update_enrollment_progress(db: Session, user_id: int, course_id: int, progress: float, last_lesson_id=None):
    enrollment = get_enrollment(db, user_id=user_id, course_id=course_id)
    if enrollment:
        enrollment.progress = progress
        if last_lesson_id:
            enrollment.last_lesson_id = last_lesson_id
        db.commit()
        db.refresh(enrollment)
    return enrollment

def get_user_enrollments(db: Session, user_id: int):
    return db.query(models.Enrollment).filter(models.Enrollment.user_id == user_id).options(joinedload(models.Enrollment.course)).all()

# Community functions
def get_posts(db: Session, skip: int = 0, limit: int = 20, sort_by: str = "latest", search: str = None, category: str = None):
    query = db.query(models.Post)
    if category:
        query = query.filter(models.Post.category == category)
    if search:
        query = query.filter(models.Post.title.contains(search) | models.Post.content.contains(search))
    if sort_by == "hottest":
        query = query.order_by(models.Post.likes_count.desc(), models.Post.created_at.desc())
    else:
        query = query.order_by(models.Post.created_at.desc())
    return query.offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.id == post_id).first()

def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(**post.dict(), author_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_comments(db: Session, post_id: int):
    return db.query(models.Comment).filter(models.Comment.post_id == post_id).all()

def get_comments_with_author(db: Session, post_id: int):
    rows = (
        db.query(models.Comment, models.User)
        .join(models.User, models.Comment.author_id == models.User.id)
        .filter(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at.asc())
        .all()
    )
    return [
        {
            "id": comment.id,
            "content": comment.content,
            "author_id": comment.author_id,
            "post_id": comment.post_id,
            "parent_id": comment.parent_id,
            "likes_count": comment.likes_count,
            "created_at": comment.created_at,
            "author_name": user.username,
            "author_avatar": user.avatar
        }
        for comment, user in rows
    ]

def get_comments_tree(db: Session, post_id: int, max_depth: int = 3):
    comments = get_comments_with_author(db, post_id)
    
    comment_map = {}
    root_comments = []
    
    for comment in comments:
        comment_id = comment["id"]
        comment_map[comment_id] = {
            **comment,
            "replies": [],
            "replies_count": 0,
            "depth": 0,
            "is_collapsed": False,
            "collapsed_replies_count": 0
        }
    
    for comment in comments:
        comment_id = comment["id"]
        parent_id = comment["parent_id"]
        comment_data = comment_map[comment_id]
        
        if parent_id is None:
            root_comments.append(comment_data)
        else:
            parent_comment = comment_map.get(parent_id)
            if parent_comment:
                depth = parent_comment["depth"] + 1
                comment_data["depth"] = depth
                parent_comment["replies"].append(comment_data)
                parent_comment["replies_count"] += 1
                
                if depth >= max_depth:
                    current_parent = parent_comment
                    while current_parent and current_parent["depth"] >= max_depth - 1:
                        current_parent["collapsed_replies_count"] += 1
                        current_parent["is_collapsed"] = True
                        current_parent = comment_map.get(current_parent["parent_id"])
    
    return root_comments

def create_comment(db: Session, comment: schemas.CommentCreate, post_id: int, user_id: int):
    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        author_id=user_id,
        parent_id=comment.parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    user = get_user(db, user_id)
    return {
        "id": db_comment.id,
        "content": db_comment.content,
        "author_id": db_comment.author_id,
        "post_id": db_comment.post_id,
        "parent_id": db_comment.parent_id,
        "likes_count": db_comment.likes_count,
        "created_at": db_comment.created_at,
        "author_name": user.username if user else "",
        "author_avatar": user.avatar if user else None
    }

def toggle_post_like(db: Session, user_id: int, post_id: int):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        return None, False
    
    existing = db.query(models.PostLike).filter(
        models.PostLike.user_id == user_id,
        models.PostLike.post_id == post_id
    ).first()
    
    if existing:
        db.delete(existing)
        post.likes_count = max(0, post.likes_count - 1)
        db.commit()
        return post, False
    else:
        db_like = models.PostLike(user_id=user_id, post_id=post_id)
        db.add(db_like)
        post.likes_count = post.likes_count + 1
        db.commit()
        db.refresh(post)
        return post, True

def toggle_comment_like(db: Session, user_id: int, comment_id: int):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        return None, False
    
    existing = db.query(models.CommentLike).filter(
        models.CommentLike.user_id == user_id,
        models.CommentLike.comment_id == comment_id
    ).first()
    
    if existing:
        db.delete(existing)
        comment.likes_count = max(0, comment.likes_count - 1)
        db.commit()
        return comment, False
    else:
        db_like = models.CommentLike(user_id=user_id, comment_id=comment_id)
        db.add(db_like)
        comment.likes_count = comment.likes_count + 1
        db.commit()
        db.refresh(comment)
        return comment, True

def get_user_likes(db: Session, user_id: int):
    post_likes = db.query(models.PostLike).filter(models.PostLike.user_id == user_id).all()
    comment_likes = db.query(models.CommentLike).filter(models.CommentLike.user_id == user_id).all()
    return {
        "post_ids": [like.post_id for like in post_likes],
        "comment_ids": [like.comment_id for like in comment_likes]
    }

# Notes functions
def get_user_notes(db: Session, user_id: int, course_id: int = None, lesson_id: int = None, search: str = None):
    from sqlalchemy import or_
    query = db.query(models.Note).filter(models.Note.user_id == user_id)
    if course_id:
        query = query.filter(models.Note.course_id == course_id)
    if lesson_id:
        query = query.filter(models.Note.lesson_id == lesson_id)
    if search:
        query = query.filter(
            or_(
                models.Note.title.contains(search),
                models.Note.content.contains(search)
            )
        )
    return query.order_by(models.Note.updated_at.desc()).all()

def get_note(db: Session, note_id: int, user_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()

def create_note(db: Session, note: schemas.NoteCreate, user_id: int):
    db_note = models.Note(**note.dict(), user_id=user_id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note_update: schemas.NoteUpdate, user_id: int):
    db_note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()
    if not db_note:
        return None
    update_data = note_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)
    db_note.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int, user_id: int):
    db_note = db.query(models.Note).filter(models.Note.id == note_id, models.Note.user_id == user_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()

# User Dashboard functions
def get_user_dashboard(db: Session, user_id: int):
    enrollments = get_user_enrollments(db, user_id)
    posts_count = db.query(models.Post).filter(models.Post.author_id == user_id).count()
    total_study_time = get_user(db, user_id).total_study_time
    return {
        "enrollments": len(enrollments),
        "completed_courses": len([e for e in enrollments if e.progress >= 100]),
        "posts_count": posts_count,
        "total_study_time": total_study_time,
        "consecutive_days": get_user(db, user_id).consecutive_days
    }

# Projects functions
def get_user_projects(db: Session, user_id: int):
    return db.query(models.UserProject).filter(models.UserProject.user_id == user_id).all()

def create_user_project(db: Session, project: schemas.UserProjectCreate, user_id: int):
    db_project = models.UserProject(**project.dict(), user_id=user_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_user_project(db: Session, project_id: int, user_id: int):
    db_project = db.query(models.UserProject).filter(models.UserProject.id == project_id, models.UserProject.user_id == user_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()

# Favorites functions
def get_user_favorites(db: Session, user_id: int):
    favorites = db.query(models.Favorite).filter(models.Favorite.user_id == user_id).options(joinedload(models.Favorite.course)).all()
    return [f.course for f in favorites]

def add_favorite(db: Session, user_id: int, course_id: int):
    existing = db.query(models.Favorite).filter(models.Favorite.user_id == user_id, models.Favorite.course_id == course_id).first()
    if not existing:
        db_favorite = models.Favorite(user_id=user_id, course_id=course_id)
        db.add(db_favorite)
        db.commit()

def remove_favorite(db: Session, user_id: int, course_id: int):
    db.query(models.Favorite).filter(models.Favorite.user_id == user_id, models.Favorite.course_id == course_id).delete()
    db.commit()

# Orders functions
def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    import time
    import random
    order_number = f"ORD{int(time.time())}{random.randint(100, 999)}"
    
    course = get_course(db, order.course_id)
    course_title = course.title if course else "Unknown Course"
    
    db_order = models.Order(
        order_number=order_number,
        user_id=user_id,
        course_id=order.course_id,
        course_title=course_title,
        total_amount=order.total_amount,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_course_reviews(db: Session, course_id: int):
    rows = (
        db.query(models.Review, models.User)
        .join(models.User, models.Review.user_id == models.User.id)
        .filter(models.Review.course_id == course_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return [
        {
            "id": review.id,
            "rating": review.rating,
            "content": review.content,
            "course_id": review.course_id,
            "user_id": review.user_id,
            "created_at": review.created_at,
            "username": user.username,
            "avatar": user.avatar
        }
        for review, user in rows
    ]

def create_review(db: Session, user_id: int, review: schemas.ReviewCreate):
    db_review = models.Review(**review.dict(), user_id=user_id)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_course_questions(db: Session, course_id: int):
    rows = (
        db.query(models.Question, models.User)
        .join(models.User, models.Question.user_id == models.User.id)
        .filter(models.Question.course_id == course_id)
        .order_by(models.Question.created_at.desc())
        .all()
    )
    return [
        {
            "id": question.id,
            "title": question.title,
            "content": question.content,
            "course_id": question.course_id,
            "user_id": question.user_id,
            "views": question.views,
            "created_at": question.created_at,
            "author_name": user.username,
            "author_avatar": user.avatar,
            "comments_count": 0,
            "answers": []
        }
        for question, user in rows
    ]

def create_question(db: Session, user_id: int, question: schemas.QuestionCreate):
    db_question = models.Question(**question.dict(), user_id=user_id)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_challenges(db: Session):
    return db.query(models.Challenge).order_by(models.Challenge.end_at.desc()).all()

def get_challenge(db: Session, challenge_id: int):
    return db.query(models.Challenge).filter(models.Challenge.id == challenge_id).first()

def get_challenge_submissions(db: Session, challenge_id: int, user_id: int = None):
    rows = (
        db.query(models.ChallengeSubmission, models.User)
        .join(models.User, models.ChallengeSubmission.user_id == models.User.id)
        .filter(models.ChallengeSubmission.challenge_id == challenge_id)
        .order_by(models.ChallengeSubmission.created_at.desc())
        .all()
    )
    user_votes = {}
    if user_id:
        votes = db.query(models.SubmissionVote).filter(
            models.SubmissionVote.user_id == user_id,
            models.SubmissionVote.submission_id.in_([r[0].id for r in rows])
        ).all()
        user_votes = {v.submission_id: v.score for v in votes}
    
    return [
        {
            "id": submission.id,
            "title": submission.title,
            "description": submission.description,
            "link": submission.link,
            "user_id": submission.user_id,
            "challenge_id": submission.challenge_id,
            "score": submission.score,
            "vote_count": submission.vote_count,
            "created_at": submission.created_at,
            "author_name": user.username,
            "author_avatar": user.avatar,
            "user_vote": user_votes.get(submission.id)
        }
        for submission, user in rows
    ]

def create_challenge_submission(db: Session, user_id: int, challenge_id: int, submission: schemas.ChallengeSubmissionCreate):
    db_submission = models.ChallengeSubmission(
        title=submission.title,
        description=submission.description,
        link=submission.link,
        user_id=user_id,
        challenge_id=challenge_id
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_challenge_submission(db: Session, submission_id: int):
    return db.query(models.ChallengeSubmission).filter(
        models.ChallengeSubmission.id == submission_id
    ).first()

def get_submission_vote(db: Session, user_id: int, submission_id: int):
    return db.query(models.SubmissionVote).filter(
        models.SubmissionVote.user_id == user_id,
        models.SubmissionVote.submission_id == submission_id
    ).first()

def create_submission_vote(db: Session, user_id: int, submission_id: int, score: int):
    from sqlalchemy import func
    
    if score < 1 or score > 5:
        return None, False
    
    submission = db.query(models.ChallengeSubmission).filter(
        models.ChallengeSubmission.id == submission_id
    ).first()
    
    if not submission:
        return None, False
    
    if submission.user_id == user_id:
        return None, False
    
    existing_vote = get_submission_vote(db, user_id, submission_id)
    if existing_vote:
        return None, False
    
    db_vote = models.SubmissionVote(
        user_id=user_id,
        submission_id=submission_id,
        score=score
    )
    db.add(db_vote)
    db.flush()
    
    result = db.query(
        func.avg(models.SubmissionVote.score),
        func.count(models.SubmissionVote.score)
    ).filter(
        models.SubmissionVote.submission_id == submission_id
    ).first()
    
    avg_score = round(result[0] or 0.0, 1)
    vote_count = result[1] or 0
    
    submission.score = avg_score
    submission.vote_count = vote_count
    
    db.commit()
    db.refresh(db_vote)
    db.refresh(submission)
    
    return {
        "submission_id": submission_id,
        "score": submission.score,
        "vote_count": submission.vote_count,
        "user_vote": score
    }, True

def get_challenge_leaderboard(db: Session, challenge_id: int, user_id: int = None):
    from sqlalchemy import func
    
    rows = (
        db.query(models.ChallengeSubmission, models.User)
        .join(models.User, models.ChallengeSubmission.user_id == models.User.id)
        .filter(models.ChallengeSubmission.challenge_id == challenge_id)
        .order_by(
            models.ChallengeSubmission.score.desc(),
            models.ChallengeSubmission.vote_count.desc(),
            models.ChallengeSubmission.created_at.asc()
        )
        .all()
    )
    
    user_votes = {}
    if user_id:
        votes = db.query(models.SubmissionVote).filter(
            models.SubmissionVote.user_id == user_id,
            models.SubmissionVote.submission_id.in_([r[0].id for r in rows])
        ).all()
        user_votes = {v.submission_id: v.score for v in votes}
    
    leaderboard = []
    for idx, (submission, user) in enumerate(rows):
        leaderboard.append({
            "id": submission.id,
            "title": submission.title,
            "description": submission.description,
            "link": submission.link,
            "user_id": submission.user_id,
            "challenge_id": submission.challenge_id,
            "score": submission.score,
            "vote_count": submission.vote_count,
            "created_at": submission.created_at,
            "author_name": user.username,
            "author_avatar": user.avatar,
            "user_vote": user_votes.get(submission.id),
            "rank": idx + 1
        })
    
    return leaderboard

def mark_lesson_complete(db: Session, user_id: int, lesson_id: int, study_duration: int = 0):
    existing = db.query(models.LessonProgress).filter(
        models.LessonProgress.user_id == user_id,
        models.LessonProgress.lesson_id == lesson_id
    ).first()
    if existing:
        if existing.completed:
            return existing, False
        existing.completed = True
        existing.study_duration = existing.study_duration + study_duration
        existing.completed_at = datetime.utcnow()
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing, True
    db_lp = models.LessonProgress(
        user_id=user_id,
        lesson_id=lesson_id,
        completed=True,
        study_duration=study_duration,
        completed_at=datetime.utcnow()
    )
    db.add(db_lp)
    db.commit()
    db.refresh(db_lp)
    return db_lp, True

def get_course_lesson_progress(db: Session, user_id: int, course_id: int):
    course = db.query(models.Course).filter(models.Course.id == course_id).options(
        joinedload(models.Course.chapters).joinedload(models.Chapter.lessons)
    ).first()
    if not course:
        return None
    lesson_ids = []
    for chapter in course.chapters:
        for lesson in chapter.lessons:
            lesson_ids.append(lesson.id)
    progress_map = {}
    if lesson_ids:
        rows = db.query(models.LessonProgress).filter(
            models.LessonProgress.user_id == user_id,
            models.LessonProgress.lesson_id.in_(lesson_ids)
        ).all()
        for row in rows:
            progress_map[row.lesson_id] = row
    total_lessons = len(lesson_ids)
    completed_lessons = sum(1 for lid in lesson_ids if lid in progress_map and progress_map[lid].completed)
    total_study_duration = sum(progress_map[lid].study_duration for lid in lesson_ids if lid in progress_map)
    progress_percentage = round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0, 1)
    chapter_progress_list = []
    for chapter in course.chapters:
        lesson_progress_list = []
        ch_completed = 0
        for lesson in chapter.lessons:
            lp = progress_map.get(lesson.id)
            is_completed = lp.completed if lp else False
            sd = lp.study_duration if lp else 0
            ca = lp.completed_at if lp else None
            if is_completed:
                ch_completed += 1
            lesson_progress_list.append(schemas.CourseLessonProgress(
                lesson_id=lesson.id,
                lesson_title=lesson.title,
                lesson_type=lesson.type,
                completed=is_completed,
                study_duration=sd,
                completed_at=ca
            ))
        chapter_progress_list.append(schemas.ChapterProgress(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            completed_count=ch_completed,
            total_count=len(chapter.lessons),
            lessons=lesson_progress_list
        ))
    return schemas.CourseProgressResponse(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        progress_percentage=progress_percentage,
        total_study_duration=total_study_duration,
        chapters=chapter_progress_list
    )

def sync_enrollment_progress(db: Session, user_id: int, course_id: int):
    progress_data = get_course_lesson_progress(db, user_id, course_id)
    if not progress_data:
        return None
    enrollment = get_enrollment(db, user_id, course_id)
    if enrollment:
        enrollment.progress = progress_data.progress_percentage
        db.commit()
        db.refresh(enrollment)
    return enrollment

def get_course_study_duration(db: Session, user_id: int, course_id: int):
    result = db.query(func.coalesce(func.sum(models.LessonProgress.study_duration), 0)).join(
        models.Lesson, models.LessonProgress.lesson_id == models.Lesson.id
    ).join(
        models.Chapter, models.Lesson.chapter_id == models.Chapter.id
    ).filter(
        models.LessonProgress.user_id == user_id,
        models.Chapter.course_id == course_id
    ).scalar()
    return result or 0

def get_user_enrollments_with_study_time(db: Session, user_id: int):
    enrollments = get_user_enrollments(db, user_id)
    course_ids = [e.course_id for e in enrollments]
    duration_map = {}
    if course_ids:
        rows = db.query(
            models.Chapter.course_id,
            func.coalesce(func.sum(models.LessonProgress.study_duration), 0)
        ).join(
            models.Lesson, models.Lesson.chapter_id == models.Chapter.id
        ).join(
            models.LessonProgress, models.LessonProgress.lesson_id == models.Lesson.id
        ).filter(
            models.LessonProgress.user_id == user_id,
            models.Chapter.course_id.in_(course_ids)
        ).group_by(models.Chapter.course_id).all()
        duration_map = {course_id: int(total or 0) for course_id, total in rows}
    return [(e, duration_map.get(e.course_id, 0)) for e in enrollments]

def get_user_code_snippets(db: Session, user_id: int):
    return db.query(models.CodeSnippet).filter(models.CodeSnippet.user_id == user_id).order_by(models.CodeSnippet.updated_at.desc()).all()

def create_code_snippet(db: Session, snippet: schemas.CodeSnippetCreate, user_id: int):
    db_snippet = models.CodeSnippet(**snippet.dict(), user_id=user_id)
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

def get_code_snippet(db: Session, snippet_id: int):
    return db.query(models.CodeSnippet).filter(models.CodeSnippet.id == snippet_id).first()

def get_code_snippet_by_share_token(db: Session, share_token: str):
    return db.query(models.CodeSnippet).filter(models.CodeSnippet.share_token == share_token).first()

def delete_code_snippet(db: Session, snippet_id: int, user_id: int):
    db_snippet = db.query(models.CodeSnippet).filter(models.CodeSnippet.id == snippet_id, models.CodeSnippet.user_id == user_id).first()
    if db_snippet:
        db.delete(db_snippet)
        db.commit()
        return True
    return False

# Achievement functions
def get_all_achievements(db: Session):
    return db.query(models.Achievement).all()

def get_user_achievements(db: Session, user_id: int):
    return db.query(models.UserAchievement).filter(
        models.UserAchievement.user_id == user_id
    ).all()

def unlock_achievement(db: Session, user_id: int, achievement_id: int):
    existing = db.query(models.UserAchievement).filter(
        models.UserAchievement.user_id == user_id,
        models.UserAchievement.achievement_id == achievement_id
    ).first()
    if existing:
        return None, False
    db_ua = models.UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id
    )
    db.add(db_ua)
    db.commit()
    db.refresh(db_ua)
    achievement = db.query(models.Achievement).filter(
        models.Achievement.id == achievement_id
    ).first()
    return achievement, True

def get_user_achievement_progress(db: Session, user_id: int):
    from sqlalchemy import func
    
    achievements = get_all_achievements(db)
    user_achievements = get_user_achievements(db, user_id)
    user_achievement_ids = {ua.achievement_id for ua in user_achievements}
    user = get_user(db, user_id)
    result = []
    
    for achievement in achievements:
        unlocked = achievement.id in user_achievement_ids
        unlocked_at = None
        if unlocked:
            for ua in user_achievements:
                if ua.achievement_id == achievement.id:
                    unlocked_at = ua.unlocked_at
                    break
        
        current_progress = 0
        progress_text = ""
        
        if achievement.condition_type == "first_login":
            current_progress = 1 if unlocked else 0
            progress_text = "首次登录即可解锁"
        elif achievement.condition_type == "completed_courses":
            enrollments = get_user_enrollments(db, user_id)
            completed = len([e for e in enrollments if e.progress >= 100])
            current_progress = min(completed, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已完成 {current_progress}/{achievement.condition_value} 门课程"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 门解锁"
        elif achievement.condition_type == "consecutive_days":
            current_progress = min(user.consecutive_days if user else 0, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已连续学习 {current_progress}/{achievement.condition_value} 天"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 天解锁"
        elif achievement.condition_type == "posts_count":
            post_count = db.query(models.Post).filter(models.Post.author_id == user_id).count()
            current_progress = min(post_count, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已发布 {current_progress}/{achievement.condition_value} 篇帖子"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 篇解锁"
        elif achievement.condition_type == "likes_received":
            posts = db.query(models.Post).filter(models.Post.author_id == user_id).all()
            comments = db.query(models.Comment).filter(models.Comment.author_id == user_id).all()
            post_likes = sum(post.likes_count for post in posts)
            comment_likes = sum(comment.likes_count for comment in comments)
            total_likes = post_likes + comment_likes
            current_progress = min(total_likes, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已获得 {current_progress}/{achievement.condition_value} 个点赞（帖子{post_likes}+评论{comment_likes}）"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 个解锁"
        elif achievement.condition_type == "study_hours":
            study_hours = (user.total_study_time if user else 0) // 3600
            current_progress = min(study_hours, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已学习 {current_progress}/{achievement.condition_value} 小时"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 小时解锁"
        elif achievement.condition_type == "all_free_courses":
            free_courses = db.query(models.Course).filter(models.Course.is_free == True).all()
            enrollments = get_user_enrollments(db, user_id)
            completed_free = len([e for e in enrollments if e.progress >= 100 and e.course.is_free])
            current_progress = min(completed_free, len(free_courses))
            total_free = len(free_courses)
            progress_text = f"已完成 {current_progress}/{total_free} 门免费课程"
            remaining = total_free - current_progress
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 门解锁"
        elif achievement.condition_type == "challenge_submissions":
            submission_count = db.query(models.ChallengeSubmission).filter(
                models.ChallengeSubmission.user_id == user_id
            ).count()
            current_progress = min(submission_count, achievement.condition_value)
            remaining = achievement.condition_value - current_progress
            progress_text = f"已提交 {current_progress}/{achievement.condition_value} 次挑战作品"
            if remaining > 0 and not unlocked:
                progress_text += f"，还差 {remaining} 次解锁"
        
        result.append({
            "achievement_id": achievement.id,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "condition_type": achievement.condition_type,
            "condition_value": achievement.condition_value,
            "unlocked": unlocked,
            "unlocked_at": unlocked_at,
            "current_progress": current_progress,
            "progress_text": progress_text
        })
    
    return result

def check_and_unlock_achievement(db: Session, user_id: int, condition_type: str, mark_notified: bool = False):
    from sqlalchemy import func
    
    progress_list = get_user_achievement_progress(db, user_id)
    newly_unlocked = []
    
    for item in progress_list:
        if item["condition_type"] == condition_type and not item["unlocked"]:
            should_unlock = False
            if condition_type == "first_login":
                should_unlock = True
            elif condition_type == "all_free_courses":
                free_courses = db.query(models.Course).filter(models.Course.is_free == True).count()
                if free_courses > 0 and item["current_progress"] >= free_courses:
                    should_unlock = True
            elif item["current_progress"] >= item["condition_value"]:
                should_unlock = True
            
            if should_unlock:
                achievement, success = unlock_achievement(db, user_id, item["achievement_id"])
                if success and achievement:
                    newly_unlocked.append(achievement)
                    if mark_notified:
                        ua = db.query(models.UserAchievement).filter(
                            models.UserAchievement.user_id == user_id,
                            models.UserAchievement.achievement_id == achievement.id
                        ).first()
                        if ua:
                            ua.notified = True
                            db.commit()
    
    return newly_unlocked

# Recommendation functions
def get_recommended_courses(db: Session, user_id: int = None, limit: int = 10):
    from sqlalchemy import func, or_
    
    if user_id is None:
        return db.query(models.Course).order_by(
            (models.Course.rating * models.Course.students_count).desc()
        ).limit(limit).all(), None, [], False
    
    enrollments = get_user_enrollments(db, user_id)
    if not enrollments:
        return db.query(models.Course).order_by(
            (models.Course.rating * models.Course.students_count).desc()
        ).limit(limit).all(), None, [], False
    
    enrolled_course_ids = [e.course_id for e in enrollments]
    
    interest_tags = set()
    level_set = set()
    recent_course = None
    
    for e in enrollments:
        if e.course and e.course.tags:
            for tag in e.course.tags:
                interest_tags.add(tag)
        if e.course and e.course.level:
            level_set.add(e.course.level)
    
    if enrollments:
        recent_enrollment = max(enrollments, key=lambda e: e.joined_at)
        recent_course = recent_enrollment.course
    
    level_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    target_levels = set()
    for lvl in level_set:
        current_order = level_order.get(lvl, 1)
        for name, order in level_order.items():
            if current_order <= order <= current_order + 1:
                target_levels.add(name)
    
    interest_tags_list = list(interest_tags)
    
    query = db.query(models.Course).filter(
        models.Course.id.notin_(enrolled_course_ids)
    )
    
    if target_levels:
        query = query.filter(models.Course.level.in_(target_levels))
    
    all_candidates = query.order_by(
        (models.Course.rating * models.Course.students_count).desc()
    ).all()
    
    recommended = []
    if interest_tags_list:
        for course in all_candidates:
            if course.tags:
                common_tags = set(course.tags) & interest_tags
                if common_tags:
                    recommended.append(course)
            if len(recommended) >= limit:
                break
    
    if not recommended:
        recommended = all_candidates[:limit]
    
    reason_course = recent_course.title if recent_course else None
    reason_tags = interest_tags_list[:3]
    
    return recommended, reason_course, reason_tags, True

def get_trending_courses(db: Session, days: int = 7, limit: int = 10):
    from sqlalchemy import func
    from datetime import timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    subquery = db.query(
        models.Enrollment.course_id,
        func.count(models.Enrollment.user_id).label("new_enrollments")
    ).filter(
        models.Enrollment.joined_at >= cutoff_date
    ).group_by(
        models.Enrollment.course_id
    ).subquery()
    
    result = db.query(
        models.Course,
        func.coalesce(subquery.c.new_enrollments, 0).label("new_enrollments")
    ).outerjoin(
        subquery, models.Course.id == subquery.c.course_id
    ).order_by(
        func.coalesce(subquery.c.new_enrollments, 0).desc(),
        (models.Course.rating * models.Course.students_count).desc()
    ).limit(limit).all()
    
    courses = []
    for course, new_enrollments in result:
        course_dict = {c.name: getattr(course, c.name) for c in course.__table__.columns}
        course_dict["new_enrollments"] = new_enrollments
        courses.append(course_dict)
    
    return courses

def get_course_discount(db: Session, course_id: int):
    now = datetime.utcnow()
    return db.query(models.CourseDiscount).filter(
        models.CourseDiscount.course_id == course_id,
        models.CourseDiscount.start_at <= now,
        models.CourseDiscount.end_at >= now
    ).first()

def get_course_with_discount(db: Session, course_id: int):
    course = get_course(db, course_id)
    if not course:
        return None
    
    discount = get_course_discount(db, course_id)
    discount_price = course.price
    
    if discount:
        discount_price = round(course.price * (1 - discount.discount_percentage / 100), 2)
    
    course_dict = {c.name: getattr(course, c.name) for c in course.__table__.columns}
    course_dict["chapters"] = course.chapters
    course_dict["current_discount"] = discount
    course_dict["discount_price"] = discount_price
    
    return course_dict

def get_courses_with_discounts(db: Session, skip: int = 0, limit: int = 100):
    courses = get_courses(db, skip=skip, limit=limit)
    result = []
    
    for course in courses:
        discount = get_course_discount(db, course.id)
        discount_price = course.price
        
        if discount:
            discount_price = round(course.price * (1 - discount.discount_percentage / 100), 2)
        
        course_dict = {c.name: getattr(course, c.name) for c in course.__table__.columns}
        course_dict["chapters"] = course.chapters
        course_dict["current_discount"] = discount
        course_dict["discount_price"] = discount_price
        result.append(course_dict)
    
    return result

def create_course_discount(db: Session, discount: schemas.CourseDiscountCreate):
    db_discount = models.CourseDiscount(**discount.dict())
    db.add(db_discount)
    db.commit()
    db.refresh(db_discount)
    return db_discount

def get_coupon_by_code(db: Session, code: str):
    return db.query(models.Coupon).filter(models.Coupon.code == code).first()

def get_coupon(db: Session, coupon_id: int):
    return db.query(models.Coupon).filter(models.Coupon.id == coupon_id).first()

def create_coupon(db: Session, coupon: schemas.CouponCreate):
    db_coupon = models.Coupon(**coupon.dict())
    db.add(db_coupon)
    db.commit()
    db.refresh(db_coupon)
    return db_coupon

def validate_coupon(db: Session, coupon_code: str, course_id: int, user_id: int = None):
    coupon = get_coupon_by_code(db, coupon_code)
    
    if not coupon:
        return False, "优惠券不存在", None
    
    if not coupon.is_active:
        return False, "优惠券已失效", None
    
    now = datetime.utcnow()
    if coupon.valid_from and now < coupon.valid_from:
        return False, "优惠券尚未生效", None
    
    if coupon.valid_until and now > coupon.valid_until:
        return False, "优惠券已过期", None
    
    if coupon.used_count >= coupon.max_uses:
        return False, "优惠券已被使用完毕", None
    
    if user_id:
        user_coupon = db.query(models.UserCoupon).filter(
            models.UserCoupon.user_id == user_id,
            models.UserCoupon.coupon_id == coupon.id
        ).first()
        
        if user_coupon and user_coupon.used_at:
            return False, "您已使用过该优惠券", None
    
    course = get_course(db, course_id)
    if not course:
        return False, "课程不存在", None
    
    discount_price = course.price
    course_discount = get_course_discount(db, course_id)
    if course_discount:
        discount_price = round(course.price * (1 - course_discount.discount_percentage / 100), 2)
    
    if discount_price < coupon.min_purchase:
        return False, f"订单金额需满 ¥{coupon.min_purchase} 才能使用该优惠券", None
    
    return True, "优惠券可用", coupon

def calculate_final_price(db: Session, course_id: int, coupon_code: str = None, user_id: int = None):
    course = get_course(db, course_id)
    if not course:
        return None
    
    original_price = course.price
    course_discount_amount = 0.0
    coupon_discount_amount = 0.0
    
    course_discount = get_course_discount(db, course_id)
    if course_discount:
        course_discount_amount = round(original_price * (course_discount.discount_percentage / 100), 2)
    
    price_after_course_discount = round(original_price - course_discount_amount, 2)
    
    coupon = None
    if coupon_code:
        valid, message, coupon_obj = validate_coupon(db, coupon_code, course_id, user_id)
        if valid and coupon_obj:
            coupon = coupon_obj
            if coupon.discount_type == "percentage":
                coupon_discount_amount = round(price_after_course_discount * (coupon.discount_value / 100), 2)
            elif coupon.discount_type == "fixed":
                coupon_discount_amount = min(coupon.discount_value, price_after_course_discount)
    
    final_price = round(price_after_course_discount - coupon_discount_amount, 2)
    if final_price < 0:
        final_price = 0
    
    return {
        "original_price": original_price,
        "course_discount": course_discount_amount,
        "discount_price": price_after_course_discount,
        "coupon_discount": coupon_discount_amount,
        "final_price": final_price,
        "coupon": coupon,
        "course_discount_obj": course_discount
    }

def claim_coupon(db: Session, user_id: int, coupon_id: int):
    coupon = get_coupon(db, coupon_id)
    if not coupon:
        return False, "优惠券不存在", None
    
    if not coupon.is_active:
        return False, "优惠券已失效", None
    
    now = datetime.utcnow()
    if coupon.valid_from and now < coupon.valid_from:
        return False, "优惠券尚未生效", None
    
    if coupon.valid_until and now > coupon.valid_until:
        return False, "优惠券已过期", None
    
    existing = db.query(models.UserCoupon).filter(
        models.UserCoupon.user_id == user_id,
        models.UserCoupon.coupon_id == coupon_id
    ).first()
    
    if existing:
        return False, "您已领取过该优惠券", None
    
    user_coupon_count = db.query(models.UserCoupon).filter(
        models.UserCoupon.coupon_id == coupon_id
    ).count()
    
    if user_coupon_count >= coupon.max_uses:
        return False, "优惠券已被领取完毕", None
    
    db_user_coupon = models.UserCoupon(
        user_id=user_id,
        coupon_id=coupon_id
    )
    db.add(db_user_coupon)
    db.commit()
    db.refresh(db_user_coupon)
    
    return True, "领取成功", db_user_coupon

def claim_coupon_by_code(db: Session, user_id: int, code: str):
    coupon = get_coupon_by_code(db, code)
    if not coupon:
        return False, "优惠券不存在", None
    
    return claim_coupon(db, user_id, coupon.id)

def get_user_coupons(db: Session, user_id: int):
    user_coupons = db.query(models.UserCoupon).filter(
        models.UserCoupon.user_id == user_id
    ).options(joinedload(models.UserCoupon.coupon)).all()
    
    now = datetime.utcnow()
    available = []
    used = []
    expired = []
    
    for uc in user_coupons:
        if uc.used_at:
            used.append(uc)
        elif uc.coupon.valid_until and now > uc.coupon.valid_until:
            expired.append(uc)
        elif not uc.coupon.is_active:
            expired.append(uc)
        else:
            available.append(uc)
    
    return {
        "available": available,
        "used": used,
        "expired": expired
    }

def mark_user_coupon_used(db: Session, user_id: int, coupon_id: int):
    user_coupon = db.query(models.UserCoupon).filter(
        models.UserCoupon.user_id == user_id,
        models.UserCoupon.coupon_id == coupon_id
    ).first()
    
    if user_coupon:
        user_coupon.used_at = datetime.utcnow()
        
        coupon = get_coupon(db, coupon_id)
        if coupon:
            coupon.used_count += 1
        
        db.commit()
        db.refresh(user_coupon)
    
    return user_coupon
