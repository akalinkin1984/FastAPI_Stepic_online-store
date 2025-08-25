# from fastapi import APIRouter
#
#
# router = APIRouter(prefix='/products', tags=['products'])
#
#
# @router.get('/')
# async def all_products():
#     pass
#
#
# @router.post('/')
# async def create_product():
#     pass
#
#
# @router.get('/{category_slug}')
# async def product_by_category(category_slug: str):
#     pass
#
#
# @router.get('/detail/{product_slug}')
# async def product_detail(product_slug: str):
#     pass
#
#
# @router.put('/{product_slug}')
# async def update_product(product_slug: str):
#     pass
#
#
# @router.delete('/{product_slug}')
# async def delete_product(product_slug: str):
#     pass


from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.schemas import CreateProduct
from app.models.category import Category
from app.models.products import Product
from app.routers.auth import get_current_user


router = APIRouter(prefix='/products', tags=['products'])


# @router.post('/', status_code=status.HTTP_201_CREATED)
# async def create_product(db: Annotated[Session, Depends(get_db)], create_product: CreateProduct):
#     category = db.scalar(select(Category).where(Category.id == create_product.category))
#     if category is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no category found'
#         )
#     db.execute(insert(Product).values(name=create_product.name,
#                                       slug=slugify(create_product.name),
#                                       description=create_product.description,
#                                       price=create_product.price,
#                                       image_url=create_product.image_url,
#                                       stock=create_product.stock,
#                                       category_id=create_product.category,
#                                       rating=0.0
#                                       ))
#     db.commit()
#     return {
#         'status_code': status.HTTP_201_CREATED,
#         'transaction': 'Successful'
#     }

# @router.post('/', status_code=status.HTTP_201_CREATED)
# async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_product: CreateProduct):
#     category = await db.scalar(select(Category).where(Category.id == create_product.category))
#     if category is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no category found'
#         )
#     await db.execute(insert(Product).values(name=create_product.name,
#                                       slug=slugify(create_product.name),
#                                       description=create_product.description,
#                                       price=create_product.price,
#                                       image_url=create_product.image_url,
#                                       stock=create_product.stock,
#                                       category_id=create_product.category,
#                                       rating=0.0
#                                       ))
#     await db.commit()
#     return {
#         'status_code': status.HTTP_201_CREATED,
#         'transaction': 'Successful'
#     }

@router.post('/')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)],
                         create_product: CreateProduct,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin') or get_user.get('is_supplier'):
        category = await db.scalar(select(Category).where(Category.id == create_product.category))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        await db.execute(insert(Category).values(insert(Product).values(name=create_product.name,
                                                                        slug=slugify(create_product.name),
                                                                        description=create_product.description,
                                                                        price=create_product.price,
                                                                        image_url=create_product.image_url,
                                                                        stock=create_product.stock,
                                                                        category_id=create_product.category,
                                                                        rating=0.0,
                                                                        supplier_id=get_user.get('id'))))
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


# @router.get('/')
# async def all_products(db: Annotated[Session, Depends(get_db)]):
#     # products = db.scalars(select(Product).where(Product.is_active == True, Product.stock > 0)).all()
#     products = db.scalars(select(Product).join(Category).where(Product.is_active == True, Category.is_active == True,
#                                                                Product.stock > 0)).all()
#     if not products:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There are no products'
#         )
#     return products

@router.get('/')
async def all_products(db: Annotated[AsyncSession, Depends(get_db)]):
    products = await db.scalars(select(Product).join(Category).where(Product.is_active == True,
                                                                     Category.is_active == True,
                                                                     Product.stock > 0))
    all_products = products.all()

    if not all_products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )
    return all_products


# @router.get('/{category_slug}')
# async def product_by_category(db: Annotated[Session, Depends(get_db)], category_slug: str):
#     category = db.scalar(select(Category).where(Category.slug == category_slug, Category.is_active == True))
#     if category is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='Category not found'
#         )
#
#     subcategories = db.scalars(select(Category).where(Category.parent_id == category.id)).all()
#     all_categories = [category.id] + [i.id for i in subcategories]
#
#     products = db.scalars(select(Product).where(Product.category_id.in_(all_categories), Product.is_active == True,
#                                                 Product.stock > 0)).all()
#     if not products:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There are no products'
#         )
#     return products

@router.get('/{category_slug}')
async def product_by_category(db: Annotated[AsyncSession, Depends(get_db)], category_slug: str):
    category = await db.scalar(select(Category).where(Category.slug == category_slug, Category.is_active == True))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found'
        )

    subcategories = await db.scalars(select(Category).where(Category.parent_id == category.id))
    all_categories = [category.id] + [i.id for i in subcategories.all()]

    products = await db.scalars(select(Product).where(Product.category_id.in_(all_categories), Product.is_active == True,
                                                Product.stock > 0))
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no products'
        )
    return products.all()


# @router.get('/detail/{product_slug}')
# async def product_detail(db: Annotated[Session, Depends(get_db)], product_slug: str):
#     product = db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True,
#                                               Product.stock > 0))
#     if not product:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no product found'
#         )
#
#     return product

@router.get('/detail/{product_slug}')
async def product_detail(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True,
                                              Product.stock > 0))
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )

    return product


# @router.put('/{product_slug}')
# async def update_product(db: Annotated[Session, Depends(get_db)], product_slug: str, update_product: CreateProduct):
#     product = db.scalar(select(Product).where(Product.slug == product_slug))
#     if product is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no product found'
#         )
#
#     category = db.scalar(select(Category).where(Category.id == update_product.category))
#     if category is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no category found'
#         )
#
#     db.execute(update(Product).where(Product.slug == product_slug).values(
#         name=update_product.name,
#         slug=slugify(update_product.name),
#         description=update_product.description,
#         price=update_product.price,
#         image_url=update_product.image_url,
#         stock=update_product.stock,
#         category_id=update_product.category))
#
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Product update is successful'
#     }

@router.put('/{product_slug}')
async def update_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         update_product_model: CreateProduct, get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        product_update = await db.scalar(select(Product).where(Product.slug == product_slug))
        if product_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        if get_user.get('id') == product_update.supplier_id or get_user.get('is_admin'):
            category = await db.scalar(select(Category).where(Category.id == update_product_model.category))
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='There is no category found'
                )
            product_update.name = update_product_model.name
            product_update.description = update_product_model.description
            product_update.price = update_product_model.price
            product_update.image_url = update_product_model.image_url
            product_update.stock = update_product_model.stock
            product_update.category_id = update_product_model.category
            product_update.slug = slugify(update_product_model.name)

            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product update is successful'
            }
        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission for this action'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )


# @router.delete('/{product_slug}')
# async def delete_product(db: Annotated[Session, Depends(get_db)], product_slug: str):
#     product = db.scalar(select(Product).where(Product.slug == product_slug, Product.is_active == True))
#     if product is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no product found'
#         )
#     db.execute(update(Product).where(Product.slug == product_slug).values(is_active=False))
#     db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Product delete is successful'
#     }

# @router.delete('/{product_slug}')
# async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
#     product = await db.scalar(select(Product).where(Product.slug == product_slug))
#     if product is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail='There is no product found'
#         )
#     product.is_active = False
#     await db.commit()
#     return {
#         'status_code': status.HTTP_200_OK,
#         'transaction': 'Product delete is successful'
#     }

@router.delete('/{product_slug}')
async def delete_product(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    product_delete = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product_delete is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
             )
    if get_user.get('is_supplier') or get_user.get('is_admin'):
        if get_user.get('id') == product_delete.supplier_id or get_user.get('is_admin'):
            product_delete.is_active = False
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'transaction': 'Product delete is successful'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You have not enough permission for this action'
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
