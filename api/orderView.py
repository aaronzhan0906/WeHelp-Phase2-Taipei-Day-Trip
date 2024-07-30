from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

class OrderView:
    @staticmethod
    def error_response(status_code, message):
        return JSONResponse(
            status_code=status_code,
            content={"error": True, "message": message}
        )

    @staticmethod
    def ok_response(status_code, order_data, token=None):
        serializable_data = jsonable_encoder(order_data)
        content = {"ok": True, "data": serializable_data}
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return JSONResponse(status_code=status_code, content=content, headers=headers)

    @staticmethod
    def format_order_data(order):
        return {
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