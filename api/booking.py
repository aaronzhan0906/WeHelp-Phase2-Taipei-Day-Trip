from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import date
import jwt
from api.user import get_user_info
from api.jwt_utils import update_jwt_payload, SECRET_KEY, ALGORITHM
from data.database import get_cursor, conn_commit, conn_close

router = APIRouter()

class BookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int


# get #
@router.get("/api/booking")
async def get_order(authorization: str = Header(...), booking: BookingInfo = None):
    try:
        if authorization == "null": 
            print("未登入")
            return JSONResponse(status_code=403, content={"error": True, "message": "Not logged in."})
        
        token = authorization.split()[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        booking = payload.get("booking")
        if not booking:
            print("No booking or empty booking")
            return JSONResponse(content={"data": None}, status_code=200)

        cursor, conn = get_cursor()
        query = "SELECT attraction_id, name, address, images FROM attractions WHERE attraction_id = %s"
        try:
            cursor.execute(query, (booking["attractionId"],))
            attraction = cursor.fetchone()
            if not attraction:
                return JSONResponse(content={"data": None}, status_code=200)
            
        except Exception as exception:
            print(f"Error fetching attraction details: {exception}")
      
        booking_detail = {
            "attraction": {
                "id": attraction[0],
                "name": attraction[1],
                "address": attraction[2],
                "image":  'https://' + attraction[3].strip('"').split('https://')[1].split('\\n')[0]
            },
            "date": booking["date"],
            "time": booking["time"],
            "price": booking["price"]
        }

        print(f"要傳到前端的JSON${booking_detail}")
        conn_close(conn)

        return JSONResponse(content={"data": booking_detail}, status_code=200)

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    


# post #
@router.post("/api/booking")
async def post_order(authorization: str = Header(...), booking: BookingInfo = None):
    
    try:
        if authorization == "null": 
            print("未登入")
            return JSONResponse(status_code=403, content={"error": True, "message": "Not logged in."})

        token = authorization.split()[1]
        if not booking:
            return JSONResponse(status_code=400, content={"error": True, "message": "建立失敗，輸入不正確或其他原因"})


        new_booking = {
            "attractionId": booking.attractionId,
            "date": str(booking.date),
            "time": booking.time,
            "price": booking.price
        }
        print(new_booking)
        print(f"post  /api/booking   ${token}")
        new_token = update_jwt_payload(token, {"booking": new_booking})

        return JSONResponse(content={"ok": True}, headers={"Authorization": f"Bearer {new_token}"}, status_code=200)

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})



# delete #
@router.delete("/api/booking")
async def delete_order(authorization: str = Header(...)):
    user_info = await get_user_info(authorization)
    if not user_info:
        raise HTTPException(status_code=403, detail={"error": True, "message": "Not logged in."})
    try:
        token = authorization.split()[1]  
        no_booking_token = update_jwt_payload(token, {"booking": None})
        print(f"DELETE {no_booking_token}")
        return JSONResponse(content={"ok": True, "message":"刪除API"}, headers={"Authorization": f"Bearer {no_booking_token}"}, status_code=200)

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})