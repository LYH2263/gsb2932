from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    avatar = Column(String, default="https://api.dicebear.com/7.x/avataaars/svg?seed=default")
    bio = Column(Text, default="")
    total_study_time = Column(Integer, default=0)
    consecutive_days = Column(Integer, default=0)
    last_study_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    enrollments = relationship("Enrollment", back_populates="user")
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    notes = relationship("Note", back_populates="user")
    user_projects = relationship("UserProject", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    orders = relationship("Order", back_populates="user")
    challenge_submissions = relationship("ChallengeSubmission", back_populates="user")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    comment_likes = relationship("CommentLike", back_populates="user", cascade="all, delete-orphan")
    code_snippets = relationship("CodeSnippet", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    level = Column(String)
    price = Column(Float, default=0.0)
    cover_image = Column(String)
    instructor = Column(String)
    rating = Column(Float, default=0.0)
    students_count = Column(Integer, default=0)
    is_free = Column(Boolean, default=True)
    tags = Column(JSON, default=list)
    chapters = relationship("Chapter", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    favorites = relationship("Favorite", back_populates="course")
    reviews = relationship("Review", back_populates="course")
    questions = relationship("Question")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    order = Column(Integer)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("Course", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    type = Column(String)
    content = Column(Text)
    video_url = Column(String, nullable=True)
    duration = Column(Integer)
    order = Column(Integer)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    chapter = relationship("Chapter", back_populates="lessons")

class Enrollment(Base):
    __tablename__ = "enrollments"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    progress = Column(Float, default=0.0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_lesson_id = Column(Integer, nullable=True)
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

class LessonProgress(Base):
    __tablename__ = "lesson_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=False)
    completed = Column(Boolean, default=False)
    study_duration = Column(Integer, default=0)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, default="discussion")
    views = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")

class PostLike(Base):
    __tablename__ = "post_likes"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    post = relationship("Post", back_populates="likes")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id])
    likes = relationship("CommentLike", back_populates="comment", cascade="all, delete-orphan")

class CommentLike(Base):
    __tablename__ = "comment_likes"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    comment = relationship("Comment", back_populates="likes")

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    difficulty = Column(String, default="Beginner")
    reward = Column(String, default="")
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    submissions = relationship("ChallengeSubmission", back_populates="challenge")

class ChallengeSubmission(Base):
    __tablename__ = "challenge_submissions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    link = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    score = Column(Float, default=0.0)
    vote_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="challenge_submissions")
    challenge = relationship("Challenge", back_populates="submissions")
    votes = relationship("SubmissionVote", back_populates="submission", cascade="all, delete-orphan")

class SubmissionVote(Base):
    __tablename__ = "submission_votes"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    submission_id = Column(Integer, ForeignKey("challenge_submissions.id"), primary_key=True)
    score = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    submission = relationship("ChallengeSubmission", back_populates="votes")

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="notes")
    lesson = relationship("Lesson")

class UserProject(Base):
    __tablename__ = "user_projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    code = Column(Text)
    language = Column(String, default="javascript")
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="user_projects")

class Favorite(Base):
    __tablename__ = "favorites"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="favorites")
    course = relationship("Course", back_populates="favorites")

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    course = relationship("Course", back_populates="reviews")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    course_title = Column(String)
    total_amount = Column(Float)
    status = Column(String, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="orders")
    course = relationship("Course")

class CodeSnippet(Base):
    __tablename__ = "code_snippets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    language = Column(String, default="python")
    is_public = Column(Boolean, default=False)
    share_token = Column(String, unique=True, default=lambda: uuid.uuid4().hex[:12])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="code_snippets")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String, nullable=False)
    condition_type = Column(String, nullable=False)
    condition_value = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_achievements = relationship("UserAchievement", back_populates="achievement")

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    notified = Column(Boolean, default=False)
    user = relationship("User")
    achievement = relationship("Achievement", back_populates="user_achievements")
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    discount_type = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    min_purchase = Column(Float, default=0.0)
    max_uses = Column(Integer, default=1)
    used_count = Column(Integer, default=0)
    valid_from = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user_coupons = relationship("UserCoupon", back_populates="coupon")

class UserCoupon(Base):
    __tablename__ = "user_coupons"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User")
    coupon = relationship("Coupon", back_populates="user_coupons")
    __table_args__ = (UniqueConstraint("user_id", "coupon_id", name="uq_user_coupon"),)

class CourseDiscount(Base):
    __tablename__ = "course_discounts"
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    discount_percentage = Column(Float, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    course = relationship("Course")
