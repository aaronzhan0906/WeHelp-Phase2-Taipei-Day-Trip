from fastapi import APIRouter, HTTPException
from api.models.mrtsModel import MRTModel
from api.views.mrtsView import MRTResponse
from api.attractions import set_sorted_mrts_names

router = APIRouter()


@router.get("/api/mrts", response_model = MRTResponse)
async def attractions():
    try:
        sorted_mrts_names = MRTModel.get_sorted_mrts()
        set_sorted_mrts_names(sorted_mrts_names)
        return {"data": sorted_mrts_names}
    
    except Exception as exception:
        raise HTTPException(status_code=500, detail={"error": True, "message": str(exception)})
