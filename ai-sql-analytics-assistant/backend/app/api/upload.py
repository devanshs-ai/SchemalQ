from fastapi import APIRouter, UploadFile, File
import pandas as pd

router = APIRouter()

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)):

    df = pd.read_csv(file.file)

    return {
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns)
    }