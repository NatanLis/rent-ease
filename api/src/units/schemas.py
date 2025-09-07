from pydantic import BaseModel, ConfigDict
from typing import Optional


class UnitBase(BaseModel):
    property_id: int
    name: str
    description: Optional[str] = None
    monthly_rent: float


class UnitCreate(UnitBase):
    """Unit response schema."""


class UnitUpdate(UnitBase):
    """Schema for updating an existing property.

    All fields are optional since updates might be partial.
    """
    property_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_rent: Optional[float] = None


class PropertyInfo(BaseModel):
    """Property info for unit response."""
    id: int
    title: str
    address: str

class UnitResponse(UnitBase):
    """Schema for unit responses.

    Includes all base fields plus the id and property info.
    """
    id: int
    property: Optional[PropertyInfo] = None
    propertyTitle: Optional[str] = None
    propertyAddress: Optional[str] = None
    activeLeases: int = 0
    status: str = "available"

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Create a copy of the object to avoid modifying the original
        data = {
            'id': obj.id,
            'property_id': obj.property_id,
            'name': obj.name,
            'description': obj.description,
            'monthly_rent': obj.monthly_rent,
            'property': None,  # We'll handle this separately
            'propertyTitle': None,
            'propertyAddress': None,
            'activeLeases': 0,
            'status': 'available'
        }
        
        # Handle the property relationship mapping
        if hasattr(obj, 'property') and obj.property:
            data['propertyTitle'] = obj.property.title
            data['propertyAddress'] = obj.property.address
            data['property'] = {
                'id': obj.property.id,
                'title': obj.property.title,
                'address': obj.property.address
            }
        
        # Calculate active leases count
        if hasattr(obj, 'leases'):
            data['activeLeases'] = len([lease for lease in obj.leases if lease.is_active])
        
        # Determine status based on active leases
        if hasattr(obj, 'leases'):
            active_leases = [lease for lease in obj.leases if lease.is_active]
            if active_leases:
                data['status'] = "occupied"
            else:
                data['status'] = "available"
        
        return cls(**data)

