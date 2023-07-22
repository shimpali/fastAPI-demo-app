from fastapi import FastAPI, HTTPException
from mongita import MongitaClientDisk
from pydantic import BaseModel

# Sample Shapes for DB
# shapes = [
#     {'item_name': 'Circle', 'no_of_sides': 1, 'id': 1},
#     {'item_name': 'Triangle', 'no_of_sides': 3, 'id': 2},
#     {'item_name': 'Octagon', 'no_of_sides': 8, 'id': 3}
# ]


app = FastAPI()

client = MongitaClientDisk()
db = client.db
shapes = db.shapes


class Shape(BaseModel):
    id: int
    item_name: str
    no_of_sides: int


@app.get('/')
async def root():
    return {'message': 'Hello World'}


@app.get('/shapes')
async def get_shapes():
    existing_shapes = shapes.find({})
    return [
        {key: shape[key] for key in shape if key != '_id'}
        for shape in existing_shapes
    ]


@app.get('/shapes/{shape_id}')
async def get_shape_by_id(shape_id: int):
    if shapes.count_documents({'id': shape_id}):
        shape = shapes.find_one({'id': shape_id})
        return {key: shape[key] for key in shape if key != '_id'}
    raise HTTPException(status_code=404, detail=f'No shape found with id={shape_id}')


@app.post('/shapes')
async def create_shape(shape: Shape):
    shapes.insert_one(shape.model_dump())
    return shape


@app.put('/shapes/{shape_id}')
async def update_shape_by_id(shape_id: int, shape: Shape):
    if shapes.count_documents({'id': shape_id}):
        shapes.replace_one({'id': shape_id}, shape.model_dump())
        return shape
    raise HTTPException(status_code=404, detail=f'No shape found with id={shape_id}')


@app.put('/shapes/upsert/{shape_id}')
async def update_shape_with_upsert(shape_id: int, shape: Shape):
    shapes.replace_one({'id': shape_id}, shape.model_dump(), upsert=True)
    return shape


@app.delete('/shapes/{shape_id}')
async def delete_shape_with_id(shape_id: int):
    deleted_shape = shapes.delete_one({'id': shape_id})
    if deleted_shape.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f'No shape found with id={shape_id}')
    return{'success': True}

