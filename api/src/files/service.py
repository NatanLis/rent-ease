from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from .repository import FileRepository
from .schemas import FileCreate, FileDownload, FileResponse


class FileService:
    """Service for file operations."""

    def __init__(self, session: AsyncSession):
        self.repository = FileRepository(session)

    async def create_file(self, file_data: FileCreate) -> FileResponse:
        """Create a new file."""
        file_obj = await self.repository.create_file(file_data)
        return FileResponse.model_validate(file_obj)

    async def get_file(self, file_id: int) -> Optional[FileResponse]:
        """Get file by ID."""
        file_obj = await self.repository.get_file(file_id)
        if file_obj:
            return FileResponse.model_validate(file_obj)
        return None

    async def get_file_for_download(self, file_id: int) -> Optional[FileDownload]:
        """Get file for download."""
        file_obj = await self.repository.get_file(file_id)
        if file_obj:
            return FileDownload(filename=file_obj.filename, mimetype=file_obj.mimetype, data=file_obj.data, size=file_obj.size)
        return None

    async def get_all_files(self) -> List[FileResponse]:
        """Get all files."""
        files = await self.repository.get_all_files()
        return [FileResponse.model_validate(file) for file in files]

    async def delete_file(self, file_id: int) -> bool:
        """Delete file by ID."""
        return await self.repository.delete_file(file_id)
