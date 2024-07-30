from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError 
from typing import List
from datetime import date
from api.userModel import UserModel
from api.JWTHandler import JWTHandler
from data.database import get_cursor, conn_close
import jwt


# model
class BookingModel:
    @staticmethod
    def get_booking_from_token(token):
        payload = jwt.decode(token, JWTHandler.SECRET_KEY, algorithms=[JWTHandler.ALGORITHM])
        return payload.get("booking")

    @staticmethod
    def get_attraction_details(attraction_id):
        cursor, conn = get_cursor()
        try:
            query = "SELECT attraction_id, name, address, images FROM attractions WHERE attraction_id = %s"
            cursor.execute(query, (attraction_id,))
            return cursor.fetchone()
        finally:
            conn_close(conn)


    
    @staticmethod
    def create_booking_detail(attraction, booking):
        return {
            "attraction": {
                "id": attraction[0],
                "name": attraction[1],
                "address": attraction[2],
                "image": 'https://' + attraction[3].strip('"').split('https://')[1].split('\\n')[0]
            },
            "date": booking["date"],
            "time": booking["time"],
            "price": booking["price"]
        }

    @staticmethod
    def create_new_booking(booking):
        return {
            "attractionId": booking.attractionId,
            "date": str(booking.date),
            "time": booking.time,
            "price": booking.price
        }

    @staticmethod
    def update_booking_token(token, booking):
        return JWTHandler.update_jwt_payload(token, {"booking": booking})


class BookingView:
    @staticmethod
    def error_response(status_code, message):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})
    
    @staticmethod
    def ok_response(status_code, data=None, token=None, message=None):
        content={"ok":True}
        if data is not None:
            content["data"] = data
        if message is not None:
            content["message"] = message
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return JSONResponse(status_code=status_code, content=content, headers=headers)




# controller

router = APIRouter()
class BookingInfo(BaseModel):
    attractionId: int
    date: date
    time: str
    price: int

def validate_booking(booking: BookingInfo) -> List[str]:
    time_slot_prices = {"morning": 2000, "afternoon": 2500}
    errors = []
    
    if booking.time not in time_slot_prices:
        errors.append("Invalid time slot")
    elif booking.price != time_slot_prices[booking.time]:
        errors.append(f"Incorrect price for {booking.time} slot")
        
    return errors


@router.get("/api/booking")
async def get_order(authorization: str = Header(...)):
    if authorization == "null":
        return BookingView.error_response(403, "Not logged in.")
    
    try:
        token = authorization.split()[1]
        booking = BookingModel.get_booking_from_token(token)
        if not booking:
            return BookingView.ok_response(200, data=None)

        attraction = BookingModel.get_attraction_details(booking["attractionId"])
        if not attraction:
            return BookingView.ok_response(200, data=None)

        booking_detail = BookingModel.create_booking_detail(attraction, booking)
        return BookingView.ok_response(200, data=booking_detail)

    except Exception as exception:
        return BookingView.error_response(500, str(exception))

@router.post("/api/booking")
async def post_order(authorization: str = Header(...), booking: BookingInfo = None):
    if authorization == "null":
        return BookingView.error_response(403, "Not logged in.")
    
    try:
        token = authorization.split()[1]
        new_booking = BookingModel.create_new_booking(booking)
        new_token = BookingModel.update_booking_token(token, new_booking)
        return BookingView.ok_response(200, token=new_token)

    except ValidationError as ve:
        error_messages = "; ".join(error["msg"] for error in ve.errors())
        return BookingView.error_response(400, f"建立失敗，輸入不正確: {error_messages}")

    except Exception as exception:
        return BookingView.error_response(500, str(exception))

@router.delete("/api/booking")
async def delete_order(authorization: str = Header(...)):
    user_info = await UserModel.get_user_info(authorization)
    if not user_info:
        return BookingView.error_response(403, "Not logged in.")
    
    try:
        token = authorization.split()[1]
        no_booking_token = BookingModel.update_booking_token(token, None)
        return BookingView.ok_response(200, message="刪除API", token=no_booking_token)

    except Exception as exception:
        return BookingView.error_response(500, str(exception))