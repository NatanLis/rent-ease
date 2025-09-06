from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel

__all__ = ["notifications"]


class NotificationAvatar(BaseModel):
    src: str


class NotificationSender(BaseModel):
    name: str
    email: Optional[str] = None
    avatar: Optional[NotificationAvatar] = None


class Notification(BaseModel):
    id: int
    unread: Optional[bool] = False
    sender: NotificationSender
    body: str
    date: str


def sub_date(dt: datetime, **kwargs) -> str:
    return (dt - timedelta(**kwargs)).isoformat()


now = datetime.now()

notifications: List[Notification] = [
    Notification(
        id=1,
        unread=True,
        sender=NotificationSender(
            name="Jordan Brown",
            email="jordan.brown@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=2"),
        ),
        body="sent you a message",
        date=sub_date(now, minutes=7),
    ),
    Notification(
        id=2,
        sender=NotificationSender(name="Lindsay Walton"),
        body="subscribed to your email list",
        date=sub_date(now, hours=1),
    ),
    Notification(
        id=3,
        unread=True,
        sender=NotificationSender(
            name="Taylor Green",
            email="taylor.green@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=3"),
        ),
        body="sent you a message",
        date=sub_date(now, hours=3),
    ),
    Notification(
        id=4,
        sender=NotificationSender(name="Courtney Henry", avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=4")),
        body="added you to a project",
        date=sub_date(now, hours=3),
    ),
    Notification(
        id=5,
        sender=NotificationSender(name="Tom Cook", avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=5")),
        body="abandonned cart",
        date=sub_date(now, hours=7),
    ),
    Notification(
        id=6,
        sender=NotificationSender(name="Casey Thomas", avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=6")),
        body="purchased your product",
        date=sub_date(now, days=1, hours=3),
    ),
    Notification(
        id=7,
        unread=True,
        sender=NotificationSender(
            name="Kelly Wilson",
            email="kelly.wilson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=8"),
        ),
        body="sent you a message",
        date=sub_date(now, days=2),
    ),
    Notification(
        id=8,
        sender=NotificationSender(
            name="Jamie Johnson",
            email="jamie.johnson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=9"),
        ),
        body="requested a refund",
        date=sub_date(now, days=5, hours=4),
    ),
    Notification(
        id=9,
        unread=True,
        sender=NotificationSender(name="Morgan Anderson", email="morgan.anderson@example.com"),
        body="sent you a message",
        date=sub_date(now, days=6),
    ),
    Notification(
        id=10, sender=NotificationSender(name="Drew Moore"), body="subscribed to your email list", date=sub_date(now, days=6)
    ),
    Notification(id=11, sender=NotificationSender(name="Riley Davis"), body="abandonned cart", date=sub_date(now, days=7)),
    Notification(
        id=12,
        sender=NotificationSender(name="Jordan Taylor"),
        body="subscribed to your email list",
        date=sub_date(now, days=9),
    ),
    Notification(
        id=13,
        sender=NotificationSender(
            name="Kelly Wilson",
            email="kelly.wilson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=8"),
        ),
        body="subscribed to your email list",
        date=sub_date(now, days=10),
    ),
    Notification(
        id=14,
        sender=NotificationSender(
            name="Jamie Johnson",
            email="jamie.johnson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=9"),
        ),
        body="subscribed to your email list",
        date=sub_date(now, days=11),
    ),
    Notification(
        id=15, sender=NotificationSender(name="Morgan Anderson"), body="purchased your product", date=sub_date(now, days=12)
    ),
    Notification(
        id=16,
        sender=NotificationSender(name="Drew Moore", avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=16")),
        body="subscribed to your email list",
        date=sub_date(now, days=13),
    ),
    Notification(
        id=17, sender=NotificationSender(name="Riley Davis"), body="subscribed to your email list", date=sub_date(now, days=14)
    ),
    Notification(
        id=18,
        sender=NotificationSender(name="Jordan Taylor"),
        body="subscribed to your email list",
        date=sub_date(now, days=15),
    ),
    Notification(
        id=19,
        sender=NotificationSender(
            name="Kelly Wilson",
            email="kelly.wilson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=8"),
        ),
        body="subscribed to your email list",
        date=sub_date(now, days=16),
    ),
    Notification(
        id=20,
        sender=NotificationSender(
            name="Jamie Johnson",
            email="jamie.johnson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=9"),
        ),
        body="purchased your product",
        date=sub_date(now, days=17),
    ),
    Notification(
        id=21, sender=NotificationSender(name="Morgan Anderson"), body="abandonned cart", date=sub_date(now, days=17)
    ),
    Notification(
        id=22, sender=NotificationSender(name="Drew Moore"), body="subscribed to your email list", date=sub_date(now, days=18)
    ),
    Notification(
        id=23, sender=NotificationSender(name="Riley Davis"), body="subscribed to your email list", date=sub_date(now, days=19)
    ),
    Notification(
        id=24,
        sender=NotificationSender(name="Jordan Taylor", avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=24")),
        body="subscribed to your email list",
        date=sub_date(now, days=20),
    ),
    Notification(
        id=25,
        sender=NotificationSender(
            name="Kelly Wilson",
            email="kelly.wilson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=8"),
        ),
        body="subscribed to your email list",
        date=sub_date(now, days=20),
    ),
    Notification(
        id=26,
        sender=NotificationSender(
            name="Jamie Johnson",
            email="jamie.johnson@example.com",
            avatar=NotificationAvatar(src="https://i.pravatar.cc/128?u=9"),
        ),
        body="abandonned cart",
        date=sub_date(now, days=21),
    ),
    Notification(
        id=27,
        sender=NotificationSender(name="Morgan Anderson"),
        body="subscribed to your email list",
        date=sub_date(now, days=22),
    ),
]
