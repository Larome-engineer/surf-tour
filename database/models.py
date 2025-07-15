from tortoise import models, fields


class Destination(models.Model):
    dest_id = fields.IntField(pk=True)
    destination = fields.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.destination


class Tour(models.Model):
    tour_id = fields.IntField(pk=True)
    tour_name = fields.CharField(max_length=255, null=False)
    tour_desc = fields.TextField(null=False)
    tour_places = fields.IntField(null=False)
    start_date = fields.CharField(max_length=10)
    start_time = fields.CharField(max_length=5)  # 'HH:MM'
    end_date = fields.CharField(max_length=10)
    tour_price = fields.FloatField(null=False)
    tour_destination = fields.ForeignKeyField(
        "models.Destination",
        related_name="tours",
        on_delete=fields.CASCADE
    )

    def __str__(self):
        return self.tour_name


class SurfLesson(models.Model):
    surf_id = fields.IntField(pk=True)
    unique_code = fields.CharField(max_length=255, null=False, unique=True)
    start_date = fields.CharField(null=False, max_length=10)
    start_time = fields.CharField(null=False, max_length=5)  # 'HH:MM'
    surf_duration = fields.TextField(null=False)
    surf_places = fields.IntField(null=False)
    surf_price = fields.FloatField(null=False)
    surf_desc = fields.TextField(null=True)
    surf_destination = fields.ForeignKeyField(
        "models.Destination",
        related_name="surf_lessons",
        on_delete=fields.CASCADE
    )
    surf_type = fields.ForeignKeyField(
        "models.LessonType",
        related_name="surf_lessons"
    )

    def __str__(self):
        return f"{self.unique_code} ({self.start_date})"


class LessonType(models.Model):
    type_id = fields.IntField(pk=True)
    type = fields.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return f"{self.type}"


class User(models.Model):
    user_id = fields.IntField(pk=True)
    user_tg_id = fields.BigIntField(null=False, unique=True)
    user_name = fields.TextField(null=True)
    user_email = fields.CharField(max_length=255, null=True, unique=True)
    user_phone = fields.CharField(max_length=255, null=True, unique=True)
    user_enable_notifications = fields.BooleanField(null=False, default=True)

    tours: fields.ReverseRelation["UserTour"]
    surfs: fields.ReverseRelation["UserSurf"]
    tour_payments: fields.ReverseRelation["TourPayment"]
    surf_payments: fields.ReverseRelation["SurfPayment"]

    def __str__(self):
        return f"User {self.user_tg_id}"


class UserTour(models.Model):
    ur_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="tours",
        on_delete=fields.CASCADE
    )
    tour = fields.ForeignKeyField(
        "models.Tour",
        related_name="user_tours",
        on_delete=fields.CASCADE
    )

    class Meta:
        unique_together = ("user", "tour")

    def __str__(self):
        return f"{self.user} | {self.tour}"


class UserSurf(models.Model):
    us_id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="surfs",
        on_delete=fields.CASCADE
    )
    surf = fields.ForeignKeyField(
        "models.SurfLesson",
        related_name="user_surfs",
        on_delete=fields.CASCADE
    )

    class Meta:
        unique_together = ("user", "surf")

    def __str__(self):
        return f"{self.user} | {self.surf}"


class TourPayment(models.Model):
    pay_id = fields.IntField(pk=True)
    pay_date = fields.CharField(null=False, max_length=10)  # 'YYYY-MM-DD'
    pay_price = fields.FloatField(null=False)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="tour_payments",
        on_delete=fields.CASCADE
    )
    tour = fields.ForeignKeyField(
        "models.Tour",
        related_name="payments",
        on_delete=fields.CASCADE
    )

    def __str__(self):
        return f"{self.user} | {self.tour} | {self.pay_price} | {self.pay_date}"


class SurfPayment(models.Model):
    pay_id = fields.IntField(pk=True)
    pay_date = fields.CharField(null=False, max_length=10)
    pay_price = fields.FloatField(null=False)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="surf_payments",
        on_delete=fields.CASCADE
    )
    surf = fields.ForeignKeyField(
        "models.SurfLesson",
        related_name="payments",
        on_delete=fields.CASCADE
    )

    def __str__(self):
        return f"{self.user} | {self.surf} | {self.pay_price} | {self.pay_date}"