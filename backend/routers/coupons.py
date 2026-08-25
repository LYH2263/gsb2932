from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud, models, schemas
from .auth import get_current_user

router = APIRouter(prefix="/coupons", tags=["coupons"])

@router.post("/claim/{code}", response_model=schemas.ClaimCouponResponse)
def claim_coupon(
    code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success, message, user_coupon = crud.claim_coupon_by_code(db, current_user.id, code)
    return {
        "success": success,
        "message": message,
        "user_coupon": user_coupon
    }

@router.get("/my", response_model=schemas.UserCouponListResponse)
def get_my_coupons(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return crud.get_user_coupons(db, current_user.id)

@router.post("/apply", response_model=schemas.ApplyCouponResponse)
def apply_coupon(
    request: schemas.ApplyCouponRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    valid, message, coupon = crud.validate_coupon(db, request.code, request.course_id, current_user.id)
    
    price_info = crud.calculate_final_price(db, request.course_id, request.code if valid else None, current_user.id)
    
    if not price_info:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "valid": valid,
        "message": message,
        "original_price": price_info["original_price"],
        "discount_price": price_info["discount_price"],
        "coupon_discount": price_info["coupon_discount"],
        "course_discount": price_info["course_discount"],
        "final_price": price_info["final_price"],
        "coupon": coupon
    }

@router.get("/course/{course_id}/discount")
def get_course_discount(
    course_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_course_with_discount(db, course_id)

@router.get("/with-discounts", response_model=List[schemas.CourseWithDiscount])
def get_courses_with_discounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.get_courses_with_discounts(db, skip=skip, limit=limit)
