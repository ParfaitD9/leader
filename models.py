import os
from datetime import datetime as dt

import peewee as pw

from settings import CURRENT_TIMEZONE

db = pw.SqliteDatabase(os.getenv("DATABASE_PATH", "database.db3"))


class BaseModel(pw.Model):
    class Meta:
        database = db


class City(BaseModel):
    name = pw.CharField(128, primary_key=True)


class Lead(BaseModel):
    name = pw.CharField(max_length=512)
    phone = pw.CharField(max_length=16, primary_key=True)
    city = pw.ForeignKeyField(City, backref="leads")
    address = pw.CharField(max_length=100)
    postal = pw.CharField(max_length=7)
    website = pw.CharField(max_length=256)
    blacklisted = pw.BooleanField(default=False)
    call_count = pw.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Lead: {self.name} at {self.phone}"

    @staticmethod
    def load(**kwargs):
        phone = kwargs.get("phone", "")
        phone = phone.split("+")[-1]
        kwargs.update({"phone": phone})
        if "city" in kwargs and isinstance(kwargs.get("city"), str):
            city, _ = City.get_or_create(name=kwargs.get("city"))
            kwargs.update({"city": city})
        return Lead.create(**kwargs)


class Call(BaseModel):
    _id = pw.PrimaryKeyField()
    timestamp = pw.DateTimeField(default=lambda: dt.now(CURRENT_TIMEZONE))
    lead = pw.ForeignKeyField(Lead, backref="calls")
    ended = pw.CharField(
        max_length=2, choices=(("BK", "Refus"), ("RV", "Rendez-vous"), ("RP", "Rappel"))
    )


class Reminder(BaseModel):
    _id = pw.PrimaryKeyField()
    created = pw.DateTimeField(default=lambda: dt.now(CURRENT_TIMEZONE))
    reminded = pw.DateTimeField(unique=True)
    lead = pw.ForeignKeyField(Lead, backref="reminders")
    is_rdv = pw.BooleanField(default=False)
    description = pw.CharField(max_length=1024)

    @staticmethod
    def load(**kwargs):
        lead: Lead = Lead.get_by_id(kwargs.get("lead"))
        print("Lead", lead.phone, "trouvé")
        kwargs.update({"lead": lead})
        return Reminder.create(**kwargs)


if __name__ == "__main__":
    db.connect()
    db.create_tables((City, Lead, Call, Reminder))
