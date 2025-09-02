from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User

from .service import FileService
from .schemas import FileResponse, FileCreate

logger = get_logger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


def get_file_service(session: AsyncSession = Depends(get_session)) -> FileService:
    """Dependency for getting file service instance."""
    return FileService(session)


@router.get("/", response_model=list[FileResponse])
async def get_all_files(
    service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
) -> list[FileResponse]:
    """Get all files."""
    logger.debug("Fetching all files")
    try:
        files = await service.get_all_files()
        logger.info(f"Retrieved {len(files)} files")
        return files
    except Exception as e:
        logger.error(f"Failed to fetch files: {str(e)}")
        raise


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Get file by ID."""
    logger.debug(f"Fetching file {file_id}")
    try:
        file_obj = await service.get_file(file_id)
        if not file_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        logger.info(f"Retrieved file {file_id}")
        return file_obj
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch file {file_id}: {str(e)}")
        raise


@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    """Upload a new file."""
    logger.debug(f"Uploading file: {file.filename}")
    try:
        # Read file data
        file_data = await file.read()
        
        # Create file object
        file_create = FileCreate(
            filename=file.filename,
            mimetype=file.content_type or "application/octet-stream",
            size=len(file_data),
            data=file_data
        )
        
        file_obj = await service.create_file(file_create)
        logger.info(f"Uploaded file {file_obj.id}: {file.filename}")
        return file_obj
    except Exception as e:
        logger.error(f"Failed to upload file {file.filename}: {str(e)}")
        raise


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
):
    """Download file by ID."""
    logger.debug(f"Downloading file {file_id}")
    try:
        file_download = await service.get_file_for_download(file_id)
        if not file_download:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        logger.info(f"Downloaded file {file_id}: {file_download.filename}")
        return Response(
            content=file_download.data,
            media_type=file_download.mimetype,
            headers={"Content-Disposition": f"attachment; filename={file_download.filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download file {file_id}: {str(e)}")
        raise


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    service: FileService = Depends(get_file_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete file by ID."""
    logger.debug(f"Deleting file {file_id}")
    try:
        success = await service.delete_file(file_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        logger.info(f"Deleted file {file_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file {file_id}: {str(e)}")
        raise
