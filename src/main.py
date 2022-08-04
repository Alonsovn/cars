from typing import List, Optional, Dict

from fastapi import FastAPI, Query, Path, HTTPException, status, Body, Request
from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from fastapi.templating import Jinja2Templates

from src.database import cars
from src.schema.carSchema import CarSchema

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request,
                                                    "title": "FastAPI - Home"})


@app.get("/cars", response_model=List[Dict[str, CarSchema]])
def get_cars(number: Optional[str] = Query("10", max_length=3)):
    response = []
    for id_car, car in list(cars.items())[:int(number)]:
        to_add = {id_car: car}
        response.append(to_add)

    return response


@app.get("/cars/{car_id}", response_model=CarSchema)
def get_car_by_id(car_id: int = Path(..., ge=0, lt=1000)):
    car = cars.get(car_id)

    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find car by Id")

    return car


@app.post("/cars", status_code=status.HTTP_201_CREATED)
def add_cars(body_cars: List[CarSchema], min_id: Optional[int] = Body(0)):
    if len(body_cars) < 1:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No cars to add")

    min_id = len(cars.values()) + min_id
    for car in body_cars:
        while cars.get(min_id):
            min_id += 1
        cars[min_id] = car
        min_id += 1

    return "Ok"


@app.put("/cars/{car_id}", response_model=Dict[str, CarSchema])
def update_car(car_id: int, car: CarSchema = Body(...)):
    stored = cars.get(car_id)
    if not stored:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Could not find car with given id")

    stored = CarSchema(**stored)
    new = car.dict(exclude_unset=True)
    new = stored.copy(update=new)
    cars[car_id] = jsonable_encoder(new)
    response = {car_id: cars[car_id]}

    return response


@app.delete("/cars/{car_id}")
def delete_car(car_id: int):
    if not cars.get(car_id):
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Could not find car with given id")

    del cars[car_id]

    return "OK"
