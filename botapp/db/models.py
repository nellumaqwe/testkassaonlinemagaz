from tortoise import fields, models

class Product(models.Model):
    id = fields.IntField(pk=True)
    collection = fields.TextField(max_length=255)
    name = fields.CharField(max_length=255)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    type = fields.TextField(max_length=255)
    picture = fields.TextField(max_length=255)

    class Meta:
        table = "products"

class Cart(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=255)
    product_name = fields.IntField(max_length=255)

    class Meta:
        table = "cart"

class Orders(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=255)
    product_name = fields.TextField(max_length=255)
    status = fields.TextField(max_length=255, default="in_proccesing")
    order_time = fields.CharField(max_length=255)

    class Meta:
        table = "orders"

class User(models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.CharField(max_length=255)
    user_username = fields.CharField(max_length=255)
    email = fields.CharField(max_length = 255)
    address = fields.CharField(max_length = 255)
    orders_id = fields.TextField(max_length=255, default=[])

    class Meta:
        table = "users"
