from fastapi import APIRouter, Header
from pydantic import BaseModel
import json
from api.JWTHandler import JWTHandler
from api.orderModel import OrderModel
from api.orderView import OrderView

router = APIRouter()

class Order(BaseModel):
    price: int 
    trip: dict
    date: str
    time: str
    contact: dict

class OrderDetail(BaseModel):
    order: Order
    prime: str

@router.post("/api/orders")
async def post_order(order_detail: OrderDetail, authorization: str = Header(...)):

    if authorization == "null": 
        return OrderView.error_response(403, "Not logged in.")
    
    if not OrderModel.validate_phone(order_detail.order.contact["phone"]):
        return OrderView.error_response(400, "訂單建立失敗，手機號碼格式錯誤")
        
    if not OrderModel.validate_email(order_detail.order.contact["email"]):
        return OrderView.error_response(400, "訂單建立失敗，電子信箱格式錯誤")
    
    try:
        token = authorization.split()[1]
        new_token = JWTHandler.remove_booking_from_jwt(token)
        user_email=JWTHandler.get_user_email(token)
        user_info = OrderModel.get_user_info_in_dict(user_email)
        order_number = OrderModel.generate_order_number()
        tappay_result = await OrderModel.process_tappay_payment(order_detail, order_number)
        response_data = await OrderModel.create_order_and_payment(order_detail, user_info, order_number, tappay_result)
        return OrderView.ok_response(200, response_data, new_token)

    except KeyError as exception:
        print(f"TapPay response missing key: {str(exception)}")
        return OrderView.error_response(500, f"TapPay response missing key: {str(exception)}")

    except Exception as exception:
        print(f"POST/API/ORDERS {str(exception)}")
        return OrderView.error_response(500, str(exception))

@router.get("/api/order/{orderNumber}")
async def get_order(orderNumber: str, authorization: str = Header(...)):
    if authorization == "null":
        return OrderView.error_response(403, "Not logged in.")
    
    try:
        order = await OrderModel.get_order(orderNumber)
        token = authorization.split()[1]
        if not JWTHandler.confirm_same_user_by_jwt(token, order[2]):
            return OrderView.error_response(403, "Unauthorized access to order.")
        
        formatted_order_data = OrderView.format_order_data(order)
        
        return OrderView.ok_response(200, formatted_order_data)
    except Exception as exception:
        return OrderView.error_response(500, str(exception))