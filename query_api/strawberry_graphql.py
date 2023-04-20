from typing import List, Optional

import strawberry
from fastapi import FastAPI
from pymongo import MongoClient
from strawberry.fastapi import GraphQLRouter

# connect to MongoDB
client = MongoClient("mongodb://admin:Embery#1234@51.161.130.170:27017")
db = client["kl_bag_ranking"]
collection = db["bag_raw"]


def item2bag(item):
    return BagItem(
        title=item['title'] if 'title' in item else None,
        price=item['price'] if 'price' in item else None,
        link=item['link'] if 'link' in item else None,
        thumbnail=item['thumbnail'] if 'thumbnail' in item else None,
        description=item['description'] if 'description' in item else None,
        images=item['images'] if 'images' in item else None,
        crawl_date=item['crawl_date'] if 'crawl_date' in item else None,
        is_AI=item['is_AI'] if 'is_AI' in item else None,
        is_sold=item['is_sold'] if 'is_sold' in item else None,
        sold_date=item['sold_date'] if 'sold_date' in item else None,
        brand=item['brand'] if 'brand' in item else None,
        model=item['model'] if 'model' in item else None,
        size=item['size'] if 'size' in item else None,
        color=item['color'] if 'color' in item else None,
        material=item['material'] if 'material' in item else None,
        hardware=item['hardware'] if 'hardware' in item else None,
        year=item['year'] if 'year' in item else None,
        measurements=item['measurements'] if 'measurements' in item else None,
        condition=item['condition'] if 'condition' in item else None,
    )


@strawberry.type
class BagItem:
    title: Optional[str]
    price: Optional[str]
    link: Optional[str]
    thumbnail: Optional[str]
    description: Optional[str]
    images: Optional[List[str]]
    crawl_date: Optional[str]
    is_AI: Optional[bool]
    is_sold: Optional[bool]
    sold_date: Optional[str]
    brand: Optional[str]
    model: Optional[str]
    size: Optional[str]
    color: Optional[str]
    material: Optional[str]
    hardware: Optional[str]
    year: Optional[str]
    measurements: Optional[str]
    condition: Optional[str]


@strawberry.type
class Query:
    bags: List[BagItem]

    @strawberry.field
    def bags(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 10,
        title: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        material: Optional[str] = None,
        hardware: Optional[str] = None,
        color: Optional[str] = None,
        size: Optional[str] = None,
        is_sold: Optional[bool] = None,
        is_AI: Optional[bool] = None,
    ) -> List[BagItem]:

        query = {}
        if title is not None:
            query['title'] = {'$regex': title, '$options': 'i'}
        if brand is not None:
            query['brand'] = {'$regex': brand, '$options': 'i'}
        if model is not None:
            query['model'] = {'$regex': model, '$options': 'i'}
        if material is not None:
            query['material'] = {'$regex': material, '$options': 'i'}
        if hardware is not None:
            query['hardware'] = {'$regex': hardware, '$options': 'i'}
        if color is not None:
            query['color'] = {'$regex': color, '$options': 'i'}
        if size is not None:
            query['size'] = {'$regex': size, '$options': 'i'}
        if is_sold is not None:
            query['is_sold'] = is_sold
        if is_AI is not None:
            query['is_AI'] = is_AI

        docs = collection.find(query).skip(offset).limit(limit)
        items = []
        for item in docs:
            bag = item2bag(item)
            items.append(bag)
        return items


schema = strawberry.Schema(query=Query)

graphql_app = GraphQLRouter(schema)
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
