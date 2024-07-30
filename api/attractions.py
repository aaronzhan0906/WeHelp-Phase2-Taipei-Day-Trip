from fastapi import *
from fastapi.responses import JSONResponse
from data.database import get_cursor, conn_commit, conn_close
from api.mrts import MRTModel
import redis
import os 
import json

# Model

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=redis_host, port = 6379, db=0)
class AttractionModel:
    @staticmethod
    def get_attractions(limit, offset, filters, params):
        cache_key = f"attractions:{limit}:{offset}:{json.dumps(filters)}:{json.dumps(params)}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        
        cursor, conn = get_cursor()
        base_query = "SELECT * FROM attractions"
        if filters:
            base_query += " WHERE " + " AND ".join(filters)
        base_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(base_query, params)
        attractions = cursor.fetchall()
        conn_commit(conn)
        conn_close(conn)

        redis_client.setex(cache_key, 259200, json.dumps(attractions))
        return attractions

    @staticmethod
    def get_total_count(filters, params):
        cache_key = f"attractions_count:{json.dumps(filters)}:{json.dumps(params)}"
        cached_count = redis_client.get(cache_key)
        if cached_count:
            return int(cached_count)

        cursor, conn = get_cursor()
        total_count_query = "SELECT COUNT(*) FROM attractions"
        if filters:
            total_count_query += " WHERE " + " AND ".join(filters)
        cursor.execute(total_count_query, params)
        count = cursor.fetchone()[0]
        conn_commit(conn)
        conn_close(conn)

        redis_client.setex(cache_key, 259200, str(count))
        return count

    @staticmethod
    def get_attraction_by_id(attraction_id):
        cache_key = f"attraction:{attraction_id}"
        cached_attraction = redis_client.get(cache_key)
        
        if cached_attraction:
            return json.loads(cached_attraction)
        
        cursor, conn = get_cursor()
        query = "SELECT * FROM attractions WHERE attraction_id = %s"
        cursor.execute(query, (attraction_id,))
        attraction = cursor.fetchone()
        conn_commit(conn)
        conn_close(conn)

        if attraction:
            redis_client.setex(cache_key, 259200, json.dumps(attraction))
        return attraction



# View
class AttractionView:
    @staticmethod
    def attraction_to_dict(attraction):
        return {
            "id": attraction[0],
            "name": attraction[1],
            "category": attraction[2],
            "description": attraction[3],
            "address": attraction[4],
            "transport": attraction[5],
            "mrt": attraction[6],
            "latitude": attraction[7],
            "longitude": attraction[8],
            "images": (lambda images_raw: 
                images_raw.strip('"').replace('\\\\','\\').split('\\n') if images_raw else []
            )(attraction[9])
        }

    @staticmethod
    def attractions_response(next_page, attractions_list):
        return JSONResponse(status_code=200, content={"nextPage": next_page, "data": attractions_list})

    @staticmethod
    def attraction_response(status_code, attraction_dict):
        return JSONResponse(status_code=status_code, content= {"data": attraction_dict})

    @staticmethod
    def error_response(status_code, message):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})



# Controller
router = APIRouter()

@router.get("/api/attractions")
async def attractions(page: int = Query(0, ge=0), keyword: str = Query(None)):
    try:
        limit = 12
        offset = page * limit
        filters = []
        params = []
       
        mrt_stations = MRTModel.get_sorted_mrts()

        if keyword:
            if keyword in mrt_stations: 
                filters.append("mrt = %s")
                params.append(keyword) 
            else:
                filters.append("name LIKE %s")
                params.append(f"%{keyword}%")
        
        total_count = AttractionModel.get_total_count(filters, params)
        attractions_tuple = AttractionModel.get_attractions(limit, offset, filters, params)
        attractions_list = [AttractionView.attraction_to_dict(attraction) for attraction in attractions_tuple]
        next_page = page + 1 if total_count >= offset + limit else None

        return AttractionView.attractions_response(next_page, attractions_list)
    
    except Exception as exception:
        print(exception)
        return AttractionView.error_response(500, str(exception))
    


@router.get("/api/attraction/{attractionId}")
async def attraction(attractionId: int):
    try:
        print(attractionId)
        attraction = AttractionModel.get_attraction_by_id(attractionId)

        if attraction:
            attraction_dict = AttractionView.attraction_to_dict(attraction)
            return AttractionView.attraction_response(200, attraction_dict)
        else:
            return AttractionView.error_response(400, "Attraction number is incorrect.")
    
    except Exception as exception:
        return AttractionView.error_response(500, str(exception))