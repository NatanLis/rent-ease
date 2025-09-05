from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from .models import File
from .schemas import FileCreate


class FileRepository:
    """Repository for file operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_file(self, file_data: FileCreate) -> File:
        """Create a new file."""
        file_obj = File(
            filename=file_data.filename,
            mimetype=file_data.mimetype,
            size=file_data.size,
            data=file_data.data
        )
        self.session.add(file_obj)
        await self.session.commit()
        await self.session.refresh(file_obj)
        return file_obj
    
    async def get_file(self, file_id: int) -> Optional[File]:
        """Get file by ID."""
        result = await self.session.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_files(self) -> List[File]:
        """Get all files."""
        result = await self.session.execute(select(File))
        return result.scalars().all()
    
    async def delete_file(self, file_id: int) -> bool:
        """Delete file by ID."""
        result = await self.session.execute(
            delete(File).where(File.id == file_id)
        )
        await self.session.commit()
        return result.rowcount > 0
