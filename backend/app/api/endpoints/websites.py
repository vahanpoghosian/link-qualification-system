from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import csv
import io
from app.db.database import get_db
from app.models.models import User, Website, Import
from app.api.endpoints.auth import get_current_user
from app.services.data_processor import process_website_data
from app.schemas.website import WebsiteResponse, ImportStatus

router = APIRouter()

@router.post("/import-csv")
async def import_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    contents = await file.read()
    csv_data = io.StringIO(contents.decode('utf-8'))
    reader = csv.DictReader(csv_data)

    websites_data = []
    for row in reader:
        if 'url' not in row or 'email' not in row or 'price' not in row:
            raise HTTPException(status_code=400, detail="CSV must have url, email, and price columns")
        websites_data.append({
            'url': row['url'].strip(),
            'email': row['email'].strip(),
            'price': float(row['price'])
        })

    import_record = Import(
        user_id=current_user.id,
        filename=file.filename,
        total_websites=len(websites_data),
        status="processing"
    )
    db.add(import_record)
    db.commit()

    background_tasks.add_task(process_website_data, websites_data, import_record.id, db)

    return {"message": f"Processing {len(websites_data)} websites", "import_id": import_record.id}

@router.get("/imports/{import_id}/status", response_model=ImportStatus)
def get_import_status(
    import_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import_record = db.query(Import).filter(
        Import.id == import_id,
        Import.user_id == current_user.id
    ).first()

    if not import_record:
        raise HTTPException(status_code=404, detail="Import not found")

    return ImportStatus(
        id=import_record.id,
        status=import_record.status,
        total_websites=import_record.total_websites,
        processed_websites=import_record.processed_websites
    )

@router.get("/", response_model=List[WebsiteResponse])
def get_websites(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    websites = db.query(Website).offset(skip).limit(limit).all()
    return websites