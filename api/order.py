from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from datetime import datetime
import re._compiler
import aiohttp
import asyncio
import re
import shortuuid
import json
from api.user import get_user_info
from api.jwt_utils import remove_booking_from_jwt, confirm_same_user_by_jwt
from data.database import get_cursor, conn_commit, conn_close

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


# post #
@router.post("/api/orders")
async def post_order(order_detail: OrderDetail, authorization: str = Header(...)):
    cursor, conn = get_cursor() 

    try:
        if authorization == "null": 
            return JSONResponse(status_code=403, content={"error": True, "message": "Not logged in."})
    
        phone_pattern = re.compile(r'^[0-9]{10}$')
        if not phone_pattern.match(order_detail.order.contact["phone"]):
            return JSONResponse(status_code=400, content={"error": True, "message": "訂單建立失敗，手機號碼格式錯誤"})
        
        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        if not email_pattern.match(order_detail.order.contact["email"]):
            return JSONResponse(status_code=400, content={"error": True, "message": "訂單建立失敗，電子信箱格式錯誤"})

        # delete booking from jwt
        token = authorization.split()[1]
        new_token = remove_booking_from_jwt(token)

        user_info_response = await get_user_info(authorization)
        user_info = json.loads(user_info_response.body)["data"]

        order_number = generate_order_number()
        user_name = user_info["name"]
        user_email = user_info["email"]


        tappay_result = await process_tappay_payment(order_detail, order_number)
        # print(tappay_result)
        payment_status = "PAID" if tappay_result["status"] == 0 else "UNPAID"
        insert_order_query = """
        INSERT INTO orders (
            order_number, payment_status, user_name, user_email, contact_name, 
            contact_email, contact_phone, attraction_id, order_date, order_time, order_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """
        order_data = (
            order_number,
            payment_status,
            user_name,
            user_email,
            order_detail.order.contact["name"],
            order_detail.order.contact["email"],
            order_detail.order.contact["phone"],
            order_detail.order.trip["id"],
            order_detail.order.date,
            order_detail.order.time,
            str(order_detail.order.price),
        )

        cursor.execute(insert_order_query, order_data)


        if payment_status == "PAID":
            insert_payment_query = """
            INSERT INTO payments (
                order_number, transaction_time_millis, payment_status, acquirer,
                rec_trade_id, bank_transaction_id, card_identifier, card_last_four,
                merchant_id, auth_code
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            payment_data = (
                tappay_result["order_number"],
                tappay_result["transaction_time_millis"],
                payment_status,
                tappay_result["acquirer"],
                tappay_result["rec_trade_id"],
                tappay_result["bank_transaction_id"],
                tappay_result["card_identifier"],
                tappay_result["card_info"]["last_four"],
                tappay_result["merchant_id"],
                tappay_result["auth_code"]
            )
            cursor.execute(insert_payment_query, payment_data)

            conn_commit(conn)

            response_data = {
                
                "number": order_number,
                "payment": {
                    "status": 0 if tappay_result["status"] == 0 else 1,
                    "message": "付款成功" if tappay_result["status"] == 0 else "付款失敗"
                }
                
            }
            # print(response_data)
        return JSONResponse(content={"ok": True, "data": response_data}, headers={"Authorization": f"Bearer {new_token}"})

    except KeyError as exception:
        print(f"TapPay response missing key: {str(exception)}")
        raise HTTPException(status_code=500, detail={"error": True, "message": f"TapPay response missing key: {str(exception)}"})

    except Exception as exception:
        print(f"exception {str(exception)}")
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)



# get #
@router.get("/api/order/{orderNumber}")
async def get_order(orderNumber: str, authorization: str = Header(...)):
    if authorization == "null":
        raise HTTPException(status=403, detail={"error": True,  "message": "Not logged in."})
    
    try:
        cursor, conn = get_cursor()
        query = """
        SELECT
            orders.order_number,
            orders.payment_status,
            orders.user_email,
            orders.contact_name,
            orders.contact_email,
            orders.contact_phone,
            orders.attraction_id,
            orders.order_date,
            orders.order_time,
            orders.order_price,
            attractions.name AS attraction_name,
            attractions.address AS attraction_address,
            attractions.images AS attraction_image
        FROM orders 
        JOIN attractions ON orders.attraction_id = attractions.attraction_id
        WHERE orders.order_number = %s
        """

        cursor.execute(query, (orderNumber,))
        order = cursor.fetchone()

        # confirm same user by email in jwt 
        token = authorization.split()[1]
        if not confirm_same_user_by_jwt(token, order[2]):
            return

        order_data = {
            "number": order[0],  
            "price": int(order[9]),  
            "trip": {
                "attraction": {
                    "id": order[6],
                    "name": order[10],
                    "address": order[11],
                    "image": 'https://' + order[12].strip('"').split('https://')[1].split('\\n')[0]
                },
                "date": order[7],
                "time": order[8]
            },
            "contact": {
                "name": order[3],
                "email": order[4],
                "phone": order[5]
            },
            "status": 0 
        } 

        return {"data": order_data}

    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
    
    finally:
        conn_close(conn)


TAPPAY_SANDBOX_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
TAPPAY_PARTNER_KEY = "partner_p1becyZviOfzZZHeDntgb8WpTLd8UsRYdp1ikOk0y7AqxiwUyQWLiguI"  
TAPPAY_MERCHANT_ID = "aaronzhan0906_GP_POS_3"  


async def process_tappay_payment(order_detail, order_number):
    headers = {
        "Content-Type": "application/json",
        "x-api-key": TAPPAY_PARTNER_KEY
    }
    payload = {
        "prime": order_detail.prime,
        "partner_key": TAPPAY_PARTNER_KEY,
        "merchant_id": TAPPAY_MERCHANT_ID,
        "details": "Taipei Day Trip Order",
        "amount": order_detail.order.price,  
        "order_number": order_number,
        "cardholder": {
            "phone_number": order_detail.order.contact["phone"],
            "name": order_detail.order.contact["name"], 
            "email": order_detail.order.contact["email"],
        },
        "remember": True 
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(TAPPAY_SANDBOX_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise Exception(f"TapPay API error: {response.status} - {error_text}")
        except aiohttp.ClientError as exception:
            raise Exception(f"Network error when contacting TapPay: {str(exception)}")
        except asyncio.TimeoutError:
            raise Exception("Request to TapPay timed out")


def generate_order_number():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    short_id = shortuuid.uuid()[:10]
    return f"{timestamp}-{short_id}"