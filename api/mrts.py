from fastapi import APIRouter
from fastapi.responses import JSONResponse
from data.database import get_cursor, conn_commit, conn_close

# Model
class MRTModel:
    @staticmethod
    def get_sorted_mrts():
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT mrt FROM taipei_attractions.sorted_mrt_attraction_counts;")
            sorted_mrts_names = [mrt[0] for mrt in cursor.fetchall() if mrt[0]]
            conn_commit(conn)
            return sorted_mrts_names
        except Exception as exception:
            raise exception
        finally:
            conn_close(conn)




# View
class MRTView:
    @staticmethod
    def ok_response(status_code, data=None):
        return JSONResponse(status_code=status_code, content=data)
    
    @staticmethod
    def error_response(status_code: int, message: str):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})




# Controller
router = APIRouter()

@router.get("/api/mrts")
async def get_mrts():
    try:
        sorted_mrts_names = MRTModel.get_sorted_mrts()
        return MRTView.ok_response(200, data={"data": sorted_mrts_names})
    except Exception as exception:
        return MRTView.error_response(500, str(exception))