from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.schemas import AddReview
from app.models.products import Product
from app.models.reviews import Review
from app.routers.auth import get_current_user


router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Review).where(Review.is_active == True))
    all_reviews = reviews.all()

    if not all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return all_reviews


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )

    reviews = await db.scalars(select(Review).where(Review.product_id == product.id, Review.is_active == True))

    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return reviews.all()


@router.post('/')
async def add_review(db: Annotated[AsyncSession, Depends(get_db)],
                         add_review: AddReview,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        product = await db.scalar(select(Product).where(Product.id == add_review.product_id))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )

        await db.execute(insert(Review).values(user_id=get_user.get('id'),
                                               product_id=product.id,
                                               comment=add_review.comment,
                                               grade=add_review.grade))

        review_list = await db.scalars(select(Review).where(Review.product_id == product.id))
        rating_list = [review.grade for review in review_list.all()]

        product.rating = sum(rating_list) / len(rating_list)

        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are not authorized to use this method'
        )


@router.delete('/{review_id}')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        review = await db.scalar(select(Review).where(Review.id == review_id))
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no review found'
            )
        review.is_active = False
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
