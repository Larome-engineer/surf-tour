from tortoise import fields
from tortoise.models import Model


class Destination(Model):
    dest_id = fields.IntField(pk=True)
    destination = fields.CharField(max_length=80, unique=True)

    tours: fields.ReverseRelation["Tour"]


class Tour(Model):
    tour_id = fields.IntField(pk=True)
    tour_name = fields.CharField(max_length=255)
    tour_desc = fields.TextField()
    tour_places = fields.IntField()
    start_date = fields.DateField()
    end_date = fields.DateField()
    tour_price = fields.DecimalField(max_digits=10, decimal_places=2)

    tour_destination = fields.ForeignKeyField(
        "models.Destination", related_name="tours",
        on_delete=fields.CASCADE
    )

    users: fields.ReverseRelation["UsersTours"]
    payments: fields.ReverseRelation["Payment"]


class User(Model):
    user_id = fields.IntField(pk=True)
    user_tg_id = fields.BigIntField(unique=True, null=False)
    user_name = fields.CharField(max_length=30)
    user_email = fields.CharField(max_length=150, unique=True)
    user_phone = fields.CharField(max_length=15, unique=True)

    tours: fields.ReverseRelation["UsersTours"]
    payments: fields.ReverseRelation["Payment"]


class UsersTours(Model):
    ur_id = fields.IntField(pk=True)

    user = fields.ForeignKeyField(
        "models.User", related_name="tours"
    )
    tour = fields.ForeignKeyField(
        "models.Tour", related_name="users"
    )

    class Meta:
        unique_together = (("user", "tour"),)


class Payment(Model):
    pay_id = fields.IntField(pk=True)
    pay_date = fields.DateField()
    pay_price = fields.DecimalField(max_digits=10, decimal_places=2)

    user = fields.ForeignKeyField(
        "models.User", related_name="payments",
    )
    tour = fields.ForeignKeyField(
        "models.Tour", related_name="payments",
    )

    class Meta:
        unique_together = (("user", "tour"),)  # Если нужно ограничение как в SQL
