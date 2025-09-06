# noqa: E501
from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from api.core.logging import get_logger

from .mails_copy import Mail, mails
from .notifications_copy import Notification, notifications

logger = get_logger(__name__)

router = APIRouter(prefix="/mock", tags=["mock"])


# ================== CUSTOMERS ==================
class Avatar(BaseModel):
    src: str


class Customer(BaseModel):
    id: int
    name: str
    email: str
    avatar: Avatar
    status: str
    location: str


@router.get("/customers", response_model=List[Customer])
async def get_customers():
    logger.debug("Fetching mock customers")
    return [
        Customer(
            id=1,
            name="Alex Smith",
            email="alex.smith@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=1"),
            status="subscribed",
            location="New York, USA",
        ),
        Customer(
            id=2,
            name="Jordan Brown",
            email="jordan.brown@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=2"),
            status="unsubscribed",
            location="London, UK",
        ),
        Customer(
            id=3,
            name="Taylor Green",
            email="taylor.green@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=3"),
            status="bounced",
            location="Paris, France",
        ),
        Customer(
            id=4,
            name="Morgan White",
            email="morgan.white@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=4"),
            status="subscribed",
            location="Berlin, Germany",
        ),
        Customer(
            id=5,
            name="Casey Gray",
            email="casey.gray@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=5"),
            status="subscribed",
            location="Tokyo, Japan",
        ),
        Customer(
            id=6,
            name="Jamie Johnson",
            email="jamie.johnson@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=6"),
            status="subscribed",
            location="Sydney, Australia",
        ),
        Customer(
            id=7,
            name="Riley Davis",
            email="riley.davis@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=7"),
            status="subscribed",
            location="New York, USA",
        ),
        Customer(
            id=8,
            name="Kelly Wilson",
            email="kelly.wilson@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=8"),
            status="subscribed",
            location="London, UK",
        ),
        Customer(
            id=9,
            name="Drew Moore",
            email="drew.moore@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=9"),
            status="bounced",
            location="Paris, France",
        ),
        Customer(
            id=10,
            name="Jordan Taylor",
            email="jordan.taylor@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=10"),
            status="subscribed",
            location="Berlin, Germany",
        ),
        Customer(
            id=11,
            name="Morgan Anderson",
            email="morgan.anderson@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=11"),
            status="subscribed",
            location="Tokyo, Japan",
        ),
        Customer(
            id=12,
            name="Casey Thomas",
            email="casey.thomas@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=12"),
            status="unsubscribed",
            location="Sydney, Australia",
        ),
        Customer(
            id=13,
            name="Jamie Jackson",
            email="jamie.jackson@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=13"),
            status="unsubscribed",
            location="New York, USA",
        ),
        Customer(
            id=14,
            name="Riley White",
            email="riley.white@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=14"),
            status="unsubscribed",
            location="London, UK",
        ),
        Customer(
            id=15,
            name="Kelly Harris",
            email="kelly.harris@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=15"),
            status="subscribed",
            location="Paris, France",
        ),
        Customer(
            id=16,
            name="Drew Martin",
            email="drew.martin@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=16"),
            status="subscribed",
            location="Berlin, Germany",
        ),
        Customer(
            id=17,
            name="Alex Thompson",
            email="alex.thompson@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=17"),
            status="unsubscribed",
            location="Tokyo, Japan",
        ),
        Customer(
            id=18,
            name="Jordan Garcia",
            email="jordan.garcia@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=18"),
            status="subscribed",
            location="Sydney, Australia",
        ),
        Customer(
            id=19,
            name="Taylor Rodriguez",
            email="taylor.rodriguez@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=19"),
            status="bounced",
            location="New York, USA",
        ),
        Customer(
            id=20,
            name="Morgan Lopez",
            email="morgan.lopez@example.com",
            avatar=Avatar(src="https://i.pravatar.cc/128?u=20"),
            status="subscribed",
            location="London, UK",
        ),
    ]


# ================== LEASES ==================
class Lease(BaseModel):
    id: int
    unitId: int
    tenantId: int
    startDate: str
    endDate: str
    isActive: bool
    tenantEmail: str
    unitName: str
    propertyTitle: str
    propertyAddress: str
    status: str


@router.get("/leases", response_model=List[Lease])
async def get_leases():
    logger.debug("Fetching mock leases")
    return [
        Lease(
            id=1,
            unitId=1,
            tenantId=1,
            startDate="2024-01-01",
            endDate="2024-12-31",
            isActive=False,
            tenantEmail="tenant1@example.com",
            unitName="A1",
            propertyTitle="Apartament w centrum",
            propertyAddress="ul. Główna 1, Warszawa",
            status="inactive",
        ),
        Lease(
            id=2,
            unitId=2,
            tenantId=2,
            startDate="2024-01-01",
            endDate="2024-12-31",
            isActive=True,
            tenantEmail="tenant2@example.com",
            unitName="A2",
            propertyTitle="Apartament w centrum",
            propertyAddress="ul. Główna 1, Warszawa",
            status="active",
        ),
        Lease(
            id=3,
            unitId=3,
            tenantId=3,
            startDate="2024-02-01",
            endDate="2025-01-31",
            isActive=True,
            tenantEmail="tenant3@example.com",
            unitName="B1",
            propertyTitle="Dom jednorodzinny",
            propertyAddress="ul. Słoneczna 15, Kraków",
            status="active",
        ),
        Lease(
            id=4,
            unitId=4,
            tenantId=4,
            startDate="2024-03-01",
            endDate="2025-02-28",
            isActive=True,
            tenantEmail="tenant4@example.com",
            unitName="B2",
            propertyTitle="Dom jednorodzinny",
            propertyAddress="ul. Słoneczna 15, Kraków",
            status="active",
        ),
        Lease(
            id=5,
            unitId=5,
            tenantId=5,
            startDate="2024-04-01",
            endDate="2025-03-31",
            isActive=True,
            tenantEmail="tenant5@example.com",
            unitName="M1",
            propertyTitle="Mieszkanie 3-pokojowe",
            propertyAddress="ul. Parkowa 8, Gdańsk",
            status="active",
        ),
        Lease(
            id=6,
            unitId=6,
            tenantId=6,
            startDate="2023-06-01",
            endDate="2024-05-31",
            isActive=False,
            tenantEmail="tenant6@example.com",
            unitName="M2",
            propertyTitle="Mieszkanie 3-pokojowe",
            propertyAddress="ul. Parkowa 8, Gdańsk",
            status="inactive",
        ),
        Lease(
            id=7,
            unitId=7,
            tenantId=7,
            startDate="2024-05-01",
            endDate="2025-04-30",
            isActive=True,
            tenantEmail="tenant7@example.com",
            unitName="C1",
            propertyTitle="Apartament premium",
            propertyAddress="ul. Nowoczesna 25, Wrocław",
            status="active",
        ),
        Lease(
            id=8,
            unitId=8,
            tenantId=8,
            startDate="2024-06-01",
            endDate="2025-05-31",
            isActive=True,
            tenantEmail="tenant8@example.com",
            unitName="C2",
            propertyTitle="Apartament premium",
            propertyAddress="ul. Nowoczesna 25, Wrocław",
            status="active",
        ),
        Lease(
            id=9,
            unitId=9,
            tenantId=9,
            startDate="2023-08-01",
            endDate="2024-07-31",
            isActive=False,
            tenantEmail="tenant9@example.com",
            unitName="D1",
            propertyTitle="Studio w centrum",
            propertyAddress="ul. Studencka 10, Poznań",
            status="inactive",
        ),
        Lease(
            id=10,
            unitId=10,
            tenantId=10,
            startDate="2024-07-01",
            endDate="2025-06-30",
            isActive=True,
            tenantEmail="tenant10@example.com",
            unitName="D2",
            propertyTitle="Studio w centrum",
            propertyAddress="ul. Studencka 10, Poznań",
            status="active",
        ),
        Lease(
            id=11,
            unitId=11,
            tenantId=1,
            startDate="2024-08-01",
            endDate="2025-07-31",
            isActive=True,
            tenantEmail="tenant1@example.com",
            unitName="E1",
            propertyTitle="Loft przemysłowy",
            propertyAddress="ul. Fabryczna 5, Łódź",
            status="active",
        ),
        Lease(
            id=12,
            unitId=12,
            tenantId=2,
            startDate="2023-09-01",
            endDate="2024-08-31",
            isActive=False,
            tenantEmail="tenant2@example.com",
            unitName="E2",
            propertyTitle="Loft przemysłowy",
            propertyAddress="ul. Fabryczna 5, Łódź",
            status="inactive",
        ),
    ]


# ================== MAILS ==================
@router.get("/mails", response_model=List[Mail])
async def get_mails():
    logger.debug("Fetching mock mails")
    return mails


# ================== MEMBERS ==================
class Member(BaseModel):
    name: str
    username: str
    role: Literal["member", "owner"]
    avatar: Avatar


members = [
    Member(
        name="Anthony Fu",
        username="antfu",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/antfu"),
    ),
    Member(
        name="Baptiste Leproux",
        username="larbish",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/larbish"),
    ),
    Member(
        name="Benjamin Canac",
        username="benjamincanac",
        role="owner",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/benjamincanac"),
    ),
    Member(
        name="Céline Dumerc",
        username="celinedumerc",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/celinedumerc"),
    ),
    Member(
        name="Daniel Roe",
        username="danielroe",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/danielroe"),
    ),
    Member(
        name="Farnabaz",
        username="farnabaz",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/farnabaz"),
    ),
    Member(
        name="Ferdinand Coumau",
        username="FerdinandCoumau",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/FerdinandCoumau"),
    ),
    Member(
        name="Hugo Richard",
        username="hugorcd",
        role="owner",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/hugorcd"),
    ),
    Member(
        name="Pooya Parsa",
        username="pi0",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/pi0"),
    ),
    Member(
        name="Sarah Moriceau",
        username="SarahM19",
        role="member",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/SarahM19"),
    ),
    Member(
        name="Sébastien Chopin",
        username="Atinux",
        role="owner",
        avatar=Avatar(src="https://ipx.nuxt.com/f_auto,s_192x192/gh_avatar/atinux"),
    ),
]


@router.get("/members", response_model=List[Member])
async def get_members():
    logger.debug("Fetching mock members")
    return members


# ================== NOTIFICATIONS ==================
@router.get("/notifications", response_model=List[Notification])
async def get_notifications():
    logger.debug("Fetching mock notifications")
    return notifications


# ================== PROPERTIES ==================
class Property(BaseModel):
    id: int
    title: str
    description: str
    address: str
    price: int
    ownerId: int
    unitsCount: int
    activeLeases: int
    status: Literal["active", "available"]


properties: List[Property] = [
    Property(
        id=1,
        title="Apartament w centrum",
        description="Nowoczesny apartament w centrum miasta",
        address="ul. Główna 1, Warszawa",
        price=2500,
        ownerId=1,
        unitsCount=2,
        activeLeases=1,
        status="active",
    ),
    Property(
        id=2,
        title="Dom jednorodzinny",
        description="Przestronny dom z ogrodem",
        address="ul. Słoneczna 15, Kraków",
        price=1800,
        ownerId=1,
        unitsCount=2,
        activeLeases=2,
        status="active",
    ),
    Property(
        id=3,
        title="Mieszkanie 3-pokojowe",
        description="Komfortowe mieszkanie w spokojnej okolicy",
        address="ul. Parkowa 8, Gdańsk",
        price=2200,
        ownerId=1,
        unitsCount=2,
        activeLeases=1,
        status="active",
    ),
    Property(
        id=4,
        title="Apartament premium",
        description="Luksusowy apartament z widokiem na miasto",
        address="ul. Nowoczesna 25, Wrocław",
        price=3500,
        ownerId=1,
        unitsCount=2,
        activeLeases=2,
        status="active",
    ),
    Property(
        id=5,
        title="Studio w centrum",
        description="Kompaktowe studio idealne dla studentów",
        address="ul. Studencka 10, Poznań",
        price=1200,
        ownerId=1,
        unitsCount=2,
        activeLeases=1,
        status="active",
    ),
    Property(
        id=6,
        title="Loft przemysłowy",
        description="Przestronny loft w stylu industrialnym",
        address="ul. Fabryczna 5, Łódź",
        price=2800,
        ownerId=1,
        unitsCount=2,
        activeLeases=1,
        status="active",
    ),
    Property(
        id=7,
        title="Kamienica zabytkowa",
        description="Odrestaurowana kamienica z duszą",
        address="ul. Stara 12, Lublin",
        price=1600,
        ownerId=1,
        unitsCount=3,
        activeLeases=0,
        status="available",
    ),
    Property(
        id=8,
        title="Apartament nad morzem",
        description="Apartament z widokiem na morze",
        address="ul. Nadmorska 7, Sopot",
        price=4200,
        ownerId=1,
        unitsCount=1,
        activeLeases=1,
        status="active",
    ),
]


@router.get("/properties", response_model=List[Property])
async def get_properties():
    logger.debug("Fetching mock properties")
    return properties


# ================== TENANTS ==================
class Tenant(BaseModel):
    id: int
    name: str
    email: str
    avatar: Optional[Avatar] = None
    status: str
    location: str


tenants: List[Tenant] = [
    Tenant(
        id=1,
        name="tenant1",
        email="tenant1@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=1"),
        status="inactive",
        location="Warszawa, Poland",
    ),
    Tenant(
        id=2,
        name="tenant2",
        email="tenant2@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=2"),
        status="active",
        location="Kraków, Poland",
    ),
    Tenant(
        id=3,
        name="tenant3",
        email="tenant3@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=3"),
        status="active",
        location="Gdańsk, Poland",
    ),
    Tenant(
        id=4,
        name="tenant4",
        email="tenant4@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=4"),
        status="inactive",
        location="Wrocław, Poland",
    ),
    Tenant(
        id=5,
        name="tenant5",
        email="tenant5@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=5"),
        status="active",
        location="Poznań, Poland",
    ),
    Tenant(
        id=6,
        name="tenant6",
        email="tenant6@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=6"),
        status="inactive",
        location="Łódź, Poland",
    ),
    Tenant(
        id=7,
        name="tenant7",
        email="tenant7@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=7"),
        status="active",
        location="Katowice, Poland",
    ),
    Tenant(
        id=8,
        name="tenant8",
        email="tenant8@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=8"),
        status="active",
        location="Lublin, Poland",
    ),
    Tenant(
        id=9,
        name="tenant9",
        email="tenant9@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=9"),
        status="inactive",
        location="Białystok, Poland",
    ),
    Tenant(
        id=10,
        name="tenant10",
        email="tenant10@example.com",
        avatar=Avatar(src="https://i.pravatar.cc/128?u=10"),
        status="active",
        location="Szczecin, Poland",
    ),
]


@router.get("/tenants", response_model=List[Tenant])
async def get_tenants():
    return tenants


# ================== UNITS ==================
class Unit(BaseModel):
    id: int
    propertyId: int
    name: str
    description: str
    monthlyRent: int
    propertyTitle: str
    propertyAddress: str
    activeLeases: int
    status: Literal["available", "occupied"]


units: List[Unit] = [
    Unit(
        id=1,
        propertyId=1,
        name="A1",
        description="Apartament 1-pokojowy z balkonem",
        monthlyRent=2500,
        propertyTitle="Apartament w centrum",
        propertyAddress="ul. Główna 1, Warszawa",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=2,
        propertyId=1,
        name="A2",
        description="Apartament 2-pokojowy z tarasem",
        monthlyRent=3000,
        propertyTitle="Apartament w centrum",
        propertyAddress="ul. Główna 1, Warszawa",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=3,
        propertyId=2,
        name="B1",
        description="Dom jednorodzinny - parter",
        monthlyRent=1800,
        propertyTitle="Dom jednorodzinny",
        propertyAddress="ul. Słoneczna 15, Kraków",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=4,
        propertyId=2,
        name="B2",
        description="Dom jednorodzinny - piętro",
        monthlyRent=2000,
        propertyTitle="Dom jednorodzinny",
        propertyAddress="ul. Słoneczna 15, Kraków",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=5,
        propertyId=3,
        name="C1",
        description="Mieszkanie 3-pokojowe - salon",
        monthlyRent=2200,
        propertyTitle="Mieszkanie 3-pokojowe",
        propertyAddress="ul. Parkowa 8, Gdańsk",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=6,
        propertyId=3,
        name="C2",
        description="Mieszkanie 3-pokojowe - sypialnia",
        monthlyRent=1800,
        propertyTitle="Mieszkanie 3-pokojowe",
        propertyAddress="ul. Parkowa 8, Gdańsk",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=7,
        propertyId=4,
        name="D1",
        description="Apartament premium - widok na miasto",
        monthlyRent=3500,
        propertyTitle="Apartament premium",
        propertyAddress="ul. Nowoczesna 25, Wrocław",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=8,
        propertyId=4,
        name="D2",
        description="Apartament premium - widok na park",
        monthlyRent=3200,
        propertyTitle="Apartament premium",
        propertyAddress="ul. Nowoczesna 25, Wrocław",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=9,
        propertyId=5,
        name="E1",
        description="Studio - kompaktowe",
        monthlyRent=1200,
        propertyTitle="Studio w centrum",
        propertyAddress="ul. Studencka 10, Poznań",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=10,
        propertyId=5,
        name="E2",
        description="Studio - przestronne",
        monthlyRent=1400,
        propertyTitle="Studio w centrum",
        propertyAddress="ul. Studencka 10, Poznań",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=11,
        propertyId=6,
        name="F1",
        description="Loft - przestronny",
        monthlyRent=2800,
        propertyTitle="Loft przemysłowy",
        propertyAddress="ul. Fabryczna 5, Łódź",
        activeLeases=1,
        status="occupied",
    ),
    Unit(
        id=12,
        propertyId=6,
        name="F2",
        description="Loft - kompaktowy",
        monthlyRent=2200,
        propertyTitle="Loft przemysłowy",
        propertyAddress="ul. Fabryczna 5, Łódź",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=13,
        propertyId=7,
        name="G1",
        description="Kamienica - parter",
        monthlyRent=1600,
        propertyTitle="Kamienica zabytkowa",
        propertyAddress="ul. Stara 12, Lublin",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=14,
        propertyId=7,
        name="G2",
        description="Kamienica - piętro",
        monthlyRent=1800,
        propertyTitle="Kamienica zabytkowa",
        propertyAddress="ul. Stara 12, Lublin",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=15,
        propertyId=7,
        name="G3",
        description="Kamienica - poddasze",
        monthlyRent=1400,
        propertyTitle="Kamienica zabytkowa",
        propertyAddress="ul. Stara 12, Lublin",
        activeLeases=0,
        status="available",
    ),
    Unit(
        id=16,
        propertyId=8,
        name="H1",
        description="Apartament nad morzem - widok na plażę",
        monthlyRent=4200,
        propertyTitle="Apartament nad morzem",
        propertyAddress="ul. Nadmorska 7, Sopot",
        activeLeases=1,
        status="occupied",
    ),
]


@router.get("/units", response_model=List[Unit])
async def get_units():
    return units


# ================== ADMIN USERS ==================
class AdminAvatar(BaseModel):
    src: str


class AdminUser(BaseModel):
    id: int
    name: str
    email: str
    role: Literal["ADMIN", "OWNER", "TENANT"]
    status: Literal["active", "inactive"]
    avatar: Optional[AdminAvatar] = None
    location: str
    createdAt: str


admin_users: List[AdminUser] = [
    AdminUser(
        id=1,
        name="Admin User",
        email="admin@rent-ease.com",
        role="ADMIN",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=admin"),
        location="Warszawa, Poland",
        createdAt="2024-01-15T10:00:00Z",
    ),
    AdminUser(
        id=2,
        name="Jan Kowalski",
        email="owner1@example.com",
        role="OWNER",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=owner1"),
        location="Kraków, Poland",
        createdAt="2024-01-20T14:30:00Z",
    ),
    AdminUser(
        id=3,
        name="Anna Nowak",
        email="owner2@example.com",
        role="OWNER",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=owner2"),
        location="Gdańsk, Poland",
        createdAt="2024-02-01T09:15:00Z",
    ),
    AdminUser(
        id=4,
        name="Piotr Wiśniewski",
        email="tenant1@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant1"),
        location="Wrocław, Poland",
        createdAt="2024-02-10T16:45:00Z",
    ),
    AdminUser(
        id=5,
        name="Maria Kowalczyk",
        email="tenant2@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant2"),
        location="Poznań, Poland",
        createdAt="2024-02-15T11:20:00Z",
    ),
    AdminUser(
        id=6,
        name="Tomasz Zieliński",
        email="tenant3@example.com",
        role="TENANT",
        status="inactive",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant3"),
        location="Łódź, Poland",
        createdAt="2024-02-20T13:10:00Z",
    ),
    AdminUser(
        id=7,
        name="Katarzyna Lewandowska",
        email="tenant4@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant4"),
        location="Katowice, Poland",
        createdAt="2024-03-01T08:30:00Z",
    ),
    AdminUser(
        id=8,
        name="Michał Dąbrowski",
        email="tenant5@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant5"),
        location="Lublin, Poland",
        createdAt="2024-03-05T15:45:00Z",
    ),
    AdminUser(
        id=9,
        name="Agnieszka Kamińska",
        email="tenant6@example.com",
        role="TENANT",
        status="inactive",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant6"),
        location="Białystok, Poland",
        createdAt="2024-03-10T12:00:00Z",
    ),
    AdminUser(
        id=10,
        name="Paweł Szymański",
        email="tenant7@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant7"),
        location="Szczecin, Poland",
        createdAt="2024-03-15T10:15:00Z",
    ),
    AdminUser(
        id=11,
        name="Magdalena Woźniak",
        email="tenant8@example.com",
        role="TENANT",
        status="active",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant8"),
        location="Gdynia, Poland",
        createdAt="2024-03-20T14:20:00Z",
    ),
    AdminUser(
        id=12,
        name="Robert Kozłowski",
        email="tenant9@example.com",
        role="TENANT",
        status="inactive",
        avatar=AdminAvatar(src="https://i.pravatar.cc/128?u=tenant9"),
        location="Radom, Poland",
        createdAt="2024-03-25T09:30:00Z",
    ),
]


@router.get("/admin/users", response_model=List[AdminUser])
async def get_admin_users():
    logger.debug("Fetching mock admin users")
    return admin_users
