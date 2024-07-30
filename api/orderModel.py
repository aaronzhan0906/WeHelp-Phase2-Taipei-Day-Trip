import re
import shortuuid
from datetime import datetime
import aiohttp
import asyncio
from data.database import get_cursor, conn_commit, conn_close

class OrderModel:
    TAPPAY_SANDBOX_URL = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
    TAPPAY_PARTNER_KEY = "partner_p1becyZviOfzZZHeDntgb8WpTLd8UsRYdp1ikOk0y7AqxiwUyQWLiguI"  
    TAPPAY_MERCHANT_ID = "aaronzhan0906_GP_POS_3"

    @staticmethod
    def validate_phone(phone):
        phone_pattern = re.compile(r'^[0-9]{10}$')
        return phone_pattern.match(phone)

    @staticmethod
    def validate_email(email):
        email_pattern = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
        return email_pattern.match(email)

    @staticmethod
    def generate_order_number():
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_id = shortuuid.uuid()[:10]
        return f"{timestamp}-{short_id}"

    @staticmethod
    async def process_tappay_payment(order_detail, order_number):
        headers = {
            "Content-Type": "application/json",
            "x-api-key": OrderModel.TAPPAY_PARTNER_KEY
        }
        payload = {
            "prime": order_detail.prime,
            "partner_key": OrderModel.TAPPAY_PARTNER_KEY,
            "merchant_id": OrderModel.TAPPAY_MERCHANT_ID,
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
                async with session.post(OrderModel.TAPPAY_SANDBOX_URL, json=payload, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"TapPay API error: {response.status} - {error_text}")
            except aiohttp.ClientError as exception:
                raise Exception(f"Network error when contacting TapPay: {str(exception)}")
            except asyncio.TimeoutError:
                raise Exception(f"Request to TapPay timed out: {str(exception)}")

    @staticmethod
    async def create_order_and_payment(order_detail, user_info, order_number, tappay_result):
        cursor, conn = get_cursor()
        try:
            payment_status = "PAID" if tappay_result["status"] == 0 else "UNPAID"
            order_data = (
                order_number,
                payment_status,
                user_info["name"],
                user_info["email"],
                order_detail.order.contact["name"],
                order_detail.order.contact["email"],
                order_detail.order.contact["phone"],
                order_detail.order.trip["id"],
                order_detail.order.date,
                order_detail.order.time,
                str(order_detail.order.price),
            )
            OrderModel.create_order(cursor, order_data)

            if payment_status == "PAID":
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
                OrderModel.create_payment(cursor, payment_data)

            conn_commit(conn)

            return {
                "number": order_number,
                "payment": {
                    "status": 0 if tappay_result["status"] == 0 else 1,
                    "message": "付款成功" if tappay_result["status"] == 0 else "付款失敗"
                }
            }
        finally:
            conn_close(conn)

    @staticmethod
    def create_order(cursor, order_data):
        insert_order_query = """
        INSERT INTO orders (
            order_number, payment_status, user_name, user_email, contact_name, 
            contact_email, contact_phone, attraction_id, order_date, order_time, order_price
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  
        """
        cursor.execute(insert_order_query, order_data)

    @staticmethod
    def create_payment(cursor, payment_data):
        insert_payment_query = """
        INSERT INTO payments (
            order_number, transaction_time_millis, payment_status, acquirer,
            rec_trade_id, bank_transaction_id, card_identifier, card_last_four,
            merchant_id, auth_code
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_payment_query, payment_data)

    @staticmethod
    async def get_order(order_number):
        cursor, conn = get_cursor()
        try:
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
            cursor.execute(query, (order_number,))
            return cursor.fetchone()
        finally:
            conn_close(conn)


    @staticmethod
    def get_user_info_in_dict(email: str) -> dict:
        cursor, conn = get_cursor()
        try:
            cursor.execute("SELECT user_id, name, email FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                return {
                    "user_id": result[0],
                    "name": result[1],
                    "email": result[2]
                }
            return None
        except Exception as exception:
            raise exception
        finally:
            conn_close(conn)