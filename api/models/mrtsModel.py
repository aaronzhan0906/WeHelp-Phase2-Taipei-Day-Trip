from fastapi import HTTPException
from data.database import get_cursor, conn_commit, conn_close

class MRTModel:
    @staticmethod # 靜態方法，不需要實例化
    def get_sorted_mrts():
        cursor, conn = get_cursor()
        cursor.execute("SELECT mrt FROM taipei_attractions.sorted_mrt_attraction_counts;")
        sorted_mrts_names = [mrt[0] for mrt in cursor.fetchall() if mrt[0]]
        conn_commit(conn)
        conn_close(conn)
        return sorted_mrts_names
        
       