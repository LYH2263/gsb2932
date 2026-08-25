from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str
    avatar: Optional[str] = None
    bio: Optional[str] = ""

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class User(UserBase):
    id: int
    is_active: bool
    total_study_time: int
    consecutive_days: int
    last_study_date: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

class LessonBase(BaseModel):
    title: str
    type: str
    content: Optional[str] = None
    video_url: Optional[str] = None
    duration: int
    order: int

class LessonCreate(LessonBase):
    pass

class Lesson(LessonBase):
    id: int
    chapter_id: int
    class Config:
        from_attributes = True

class ChapterBase(BaseModel):
    title: str
    order: int

class ChapterCreate(ChapterBase):
    lessons: List[LessonCreate] = []

class Chapter(ChapterBase):
    id: int
    course_id: int
    lessons: List[Lesson] = []
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: str
    level: str
    price: float
    cover_image: Optional[str] = None
    instructor: str
    rating: float = 0.0
    students_count: int = 0
    is_free: bool = True
    tags: Optional[List[str]] = []

class CourseCreate(CourseBase):
    chapters: List[ChapterCreate] = []

class Course(CourseBase):
    id: int
    chapters: List[Chapter] = []
    class Config:
        from_attributes = True

class EnrollmentBase(BaseModel):
    progress: float = 0.0

class EnrollmentUpdate(EnrollmentBase):
    last_lesson_id: Optional[int] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class Enrollment(EnrollmentBase):
    user_id: int
    course_id: int
    joined_at: datetime
    last_lesson_id: Optional[int] = None
    course: Optional[Course] = None
    class Config:
        from_attributes = True

class LessonProgressBase(BaseModel):
    completed: bool = False
    study_duration: int = 0

class LessonProgressCreate(LessonProgressBase):
    lesson_id: int
    study_duration: int = 0

class LessonProgressMarkComplete(BaseModel):
    study_duration: int = 0

class LessonProgress(LessonProgressBase):
    id: int
    user_id: int
    lesson_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class LessonProgressWithLesson(LessonProgress):
    lesson_title: Optional[str] = None
    lesson_type: Optional[str] = None

class CourseLessonProgress(BaseModel):
    lesson_id: int
    lesson_title: str
    lesson_type: str
    completed: bool
    study_duration: int
    completed_at: Optional[datetime] = None

class ChapterProgress(BaseModel):
    chapter_id: int
    chapter_title: str
    completed_count: int
    total_count: int
    lessons: List[CourseLessonProgress]

class CourseProgressResponse(BaseModel):
    course_id: int
    total_lessons: int
    completed_lessons: int
    progress_percentage: float
    total_study_duration: int
    chapters: List[ChapterProgress]

class PostBase(BaseModel):
    title: str
    content: str
    category: str = "discussion"

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    author_id: int
    views: int
    likes_count: int
    created_at: datetime
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    parent_id: Optional[int] = None

class Comment(CommentBase):
    id: int
    author_id: int
    post_id: int
    parent_id: Optional[int] = None
    likes_count: int
    created_at: datetime
    class Config:
        from_attributes = True

class CommentWithAuthor(CommentBase):
    id: int
    author_id: int
    post_id: int
    parent_id: Optional[int] = None
    likes_count: int
    created_at: datetime
    author_name: str
    author_avatar: Optional[str] = None
    class Config:
        from_attributes = True

class CommentTree(CommentWithAuthor):
    replies: List['CommentTree'] = []
    replies_count: int = 0
    depth: int = 0
    is_collapsed: bool = False
    collapsed_replies_count: int = 0

CommentTree.model_rebuild()

class PostLike(BaseModel):
    user_id: int
    post_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CommentLike(BaseModel):
    user_id: int
    comment_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LikeStatusResponse(BaseModel):
    post_ids: List[int]
    comment_ids: List[int]

class NoteBase(BaseModel):
    title: str
    content: str
    course_id: int
    lesson_id: Optional[int] = None

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    course_id: Optional[int] = None
    lesson_id: Optional[int] = None

class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class UserProjectBase(BaseModel):
    title: str
    code: str
    language: str = "javascript"

class UserProjectCreate(UserProjectBase):
    pass

class UserProject(UserProjectBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    pass

class FavoriteCreate(FavoriteBase):
    pass

class Favorite(FavoriteBase):
    user_id: int
    course_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    rating: int
    content: str
    course_id: int

class ReviewCreate(ReviewBase):
    pass

class Review(ReviewBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ReviewDetail(ReviewBase):
    id: int
    user_id: int
    username: str
    avatar: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class AnswerDetail(BaseModel):
    id: int
    content: str
    author_name: str
    author_avatar: Optional[str] = None
    created_at: datetime

class QuestionBase(BaseModel):
    title: str
    content: str
    course_id: int

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    user_id: int
    views: int
    created_at: datetime
    class Config:
        from_attributes = True

class QuestionDetail(Question):
    author_name: str
    author_avatar: Optional[str] = None
    comments_count: int = 0
    answers: List[AnswerDetail] = []

class ChallengeBase(BaseModel):
    title: str
    description: str
    difficulty: str
    reward: str
    start_at: datetime
    end_at: datetime

class ChallengeCreate(ChallengeBase):
    pass

class Challenge(ChallengeBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ChallengeSubmissionBase(BaseModel):
    title: str
    description: str
    link: Optional[str] = None

class ChallengeSubmissionCreate(ChallengeSubmissionBase):
    pass

class ChallengeSubmission(ChallengeSubmissionBase):
    id: int
    user_id: int
    challenge_id: int
    score: float
    vote_count: int = 0
    created_at: datetime
    class Config:
        from_attributes = True

class ChallengeSubmissionDetail(ChallengeSubmission):
    author_name: str
    author_avatar: Optional[str] = None
    user_vote: Optional[int] = None

class ChallengeDetail(Challenge):
    submissions: List[ChallengeSubmissionDetail] = []

class SubmissionVoteCreate(BaseModel):
    score: int

class SubmissionVote(BaseModel):
    user_id: int
    submission_id: int
    score: int
    created_at: datetime
    class Config:
        from_attributes = True

class SubmissionVoteResponse(BaseModel):
    submission_id: int
    score: float
    vote_count: int
    user_vote: int

class LeaderboardEntry(BaseModel):
    id: int
    title: str
    description: str
    link: Optional[str] = None
    user_id: int
    challenge_id: int
    score: float
    vote_count: int
    created_at: datetime
    author_name: str
    author_avatar: Optional[str] = None
    rank: int

class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]

class OrderBase(BaseModel):
    total_amount: float
    status: str = "completed"

class OrderCreate(OrderBase):
    course_id: int

class Order(OrderBase):
    id: int
    order_number: str
    user_id: int
    course_id: Optional[int] = None
    course_title: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CodeSnippetCreate(BaseModel):
    title: str
    code: str
    language: str = "python"
    is_public: bool = False

class CodeSnippetUpdate(BaseModel):
    title: Optional[str] = None
    code: Optional[str] = None
    language: Optional[str] = None
    is_public: Optional[bool] = None

class CodeSnippet(BaseModel):
    id: int
    user_id: int
    title: str
    code: str
    language: str
    is_public: bool
    share_token: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class SharedCodeSnippet(BaseModel):
    id: int
    title: str
    code: str
    language: str
    share_token: str
    created_at: datetime
    author_name: str
    author_avatar: Optional[str] = None

class AchievementBase(BaseModel):
    name: str
    description: str
    icon: str
    condition_type: str
    condition_value: int = 1

class AchievementCreate(AchievementBase):
    pass

class Achievement(AchievementBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class UserAchievementBase(BaseModel):
    user_id: int
    achievement_id: int

class UserAchievement(UserAchievementBase):
    id: int
    unlocked_at: datetime
    achievement: Achievement
    class Config:
        from_attributes = True

class UserAchievementResponse(BaseModel):
    achievement_id: int
    name: str
    description: str
    icon: str
    condition_type: str
    condition_value: int
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    current_progress: int
    progress_text: str

class AchievementUnlockResponse(BaseModel):
    unlocked: bool
    achievement: Optional[Achievement] = None

class CourseWithNewEnrollments(Course):
    new_enrollments: int = 0

class RecommendedCourseResponse(BaseModel):
    courses: List[Course]
    reason_course: Optional[str] = None
    reason_tags: List[str] = []
    is_personalized: bool = False

class CouponBase(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    min_purchase: float = 0.0
    max_uses: int = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = True

class CouponCreate(CouponBase):
    pass

class Coupon(CouponBase):
    id: int
    used_count: int = 0
    class Config:
        from_attributes = True

class UserCouponBase(BaseModel):
    coupon_id: int

class UserCouponCreate(UserCouponBase):
    pass

class UserCoupon(UserCouponBase):
    id: int
    user_id: int
    used_at: Optional[datetime] = None
    created_at: datetime
    coupon: Coupon
    class Config:
        from_attributes = True

class CourseDiscountBase(BaseModel):
    course_id: int
    discount_percentage: float
    start_at: datetime
    end_at: datetime

class CourseDiscountCreate(CourseDiscountBase):
    pass

class CourseDiscount(CourseDiscountBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CourseWithDiscount(Course):
    current_discount: Optional[CourseDiscount] = None
    discount_price: Optional[float] = None

class ApplyCouponRequest(BaseModel):
    code: str
    course_id: int

class ApplyCouponResponse(BaseModel):
    valid: bool
    message: str
    original_price: float
    discount_price: float
    coupon_discount: float
    course_discount: float
    final_price: float
    coupon: Optional[Coupon] = None

class ClaimCouponResponse(BaseModel):
    success: bool
    message: str
    user_coupon: Optional[UserCoupon] = None

class UserCouponListResponse(BaseModel):
    available: List[UserCoupon] = []
    used: List[UserCoupon] = []
    expired: List[UserCoupon] = []
