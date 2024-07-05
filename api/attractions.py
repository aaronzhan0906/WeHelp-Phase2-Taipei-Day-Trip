from fastapi import *
from fastapi.responses import JSONResponse
from data.database import get_cursor, conn_commit, conn_close
router = APIRouter()
sorted_mrts_names = []

@router.get("/api/attractions")
async def attractions(page: int = Query(0, ge=0), keyword: str = Query(None)):
    try:
        cursor, conn = get_cursor()
        limit = 12
        offset = page * limit
        base_query = "SELECT * FROM attractions"
        total_count_query = "SELECT COUNT(*) FROM attractions"
        filters = []
        params = []
        
        mrt_stations = [mrt[0] for mrt in get_sorted_mrts_names()]

        if keyword:
            if keyword in mrt_stations: 
                filters.append("mrt = %s")
                params.append(keyword) 
            else:
                print(f"{keyword} 不存在tuple。")
                filters.append("name LIKE %s")
                params.append(f"%{keyword}%")
        
        if filters:
            base_query += " WHERE " + " AND ".join(filters)

        # Count query
        if filters:
            total_count_query = "SELECT COUNT(*) FROM attractions WHERE " + " AND ".join(filters)
        else:
            total_count_query = "SELECT COUNT(*) FROM attractions"
        
        cursor.execute(total_count_query, params)
        total_count = cursor.fetchone()[0]

        # Search
        base_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(base_query, params)
        attractions_tuple = cursor.fetchall()

        attractions_list = []
        for attraction in attractions_tuple:
            attraction_dict = {
                "id": attraction[0],
                "name": attraction[1],
                "category": attraction[2],
                "description": attraction[3],
                "address": attraction[4],
                "transport": attraction[5],
                "mrt": attraction[6],
                "latitude": (attraction[7]),
                "longitude": (attraction[8]),
                "images": process_images(attraction[9])
            }
            attractions_list.append(attraction_dict)
        if total_count >= offset + limit:
            next_page = page + 1 
        else:
            next_page = None

        return JSONResponse(content={"nextPage": next_page, "data": attractions_list}, status_code=200)
    
    except Exception as exception:
        return JSONResponse(content={"error": True, "message": str(exception)}, status_code=500)
    
    finally:
        conn_commit(conn)
        conn_close(conn)



@router.get("/api/attraction/{attractionId}")
async def attractions(attractionId: int):
    try:
        cursor, conn = get_cursor()
        query = "SELECT * FROM attractions WHERE attraction_id = %s"
        cursor.execute(query, (attractionId,))
        attraction = cursor.fetchone()

        if attraction:
            attraction_dict = {
                "id": attraction[0],
                "name": attraction[1],
                "category": attraction[2],
                "description": attraction[3],
                "address": attraction[4],
                "transport": attraction[5],
                "mrt": attraction[6],
                "latitude": (attraction[7]),
                "longitude": (attraction[8]),
                "images": process_images(attraction[9])
            }
            return JSONResponse({"data": attraction_dict}, status_code=200)
        else:
            return JSONResponse({"error": True, "message": "Attraction number is incorrect."}, status_code=400)
    
    except Exception as exception:
        return JSONResponse(content={"error": True, "message": str(exception)}, status_code=500)
    
    finally:
        conn_commit(conn)
        conn_close(conn)
    

def process_images(images_raw):
    images_list = []
    if images_raw:
        images_raw = images_raw.strip('"').replace('\\\\','\\')
        images_list = images_raw.split('\\n')
        return images_list


def set_sorted_mrts_names(names):
    global sorted_mrts_names
    sorted_mrts_names = names

def get_sorted_mrts_names():
    return sorted_mrts_names