from fastapi.responses import JSONResponse




# View
class UserView:
    @staticmethod
    def error_response(status_code: int, message: str):
        return JSONResponse(status_code=status_code, content={"error": True, "message": message})

    @staticmethod
    def ok_response(status_code: int, message: str, data: dict = None, token: str = None):
        content = {"ok": True, "message": message}
        if data:
            content["data"] = data
        if token:
            content["token"] = token
        headers = {"Authorization": f"Bearer {token}"} if token else None
        return JSONResponse(status_code=status_code, content=content, headers=headers)




