from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        EMPLOYEE = "EMPLOYEE", "Employee / Pharmacist"
        CLIENT = "CLIENT", "Client / Customer"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CLIENT)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def is_employee_or_admin(self):
        return self.role in [self.Role.EMPLOYEE, self.Role.ADMIN] or self.is_superuser


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories'
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} -> {self.name}"
        return self.name


class ActiveIngredient(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company_name or self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    active_ingredient = models.ForeignKey(
        ActiveIngredient, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    description = models.TextField(blank=True, null=True)
    
    # Packaging & Multi-Unit Specifications
    package_unit = models.CharField(max_length=50, default="Box", help_text="e.g. Box, Bottle")
    sub_unit = models.CharField(max_length=50, default="Strip", help_text="e.g. Strip, Tablet, Ampoule")
    units_per_package = models.PositiveIntegerField(default=1)

    # Pricing
    package_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sub_unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    # Inventory tracked in smallest unit (sub_units)
    stock_in_sub_units = models.PositiveIntegerField(default=0)

    # Status & Soft Delete
    requires_prescription = models.BooleanField(default=False)
    is_visible_in_catalog = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_packages_in_stock(self):
        if self.units_per_package > 0:
            return round(self.stock_in_sub_units / self.units_per_package, 2)
        return 0

    def __str__(self):
        return self.name


class PurchaseOrder(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, related_name="purchase_orders")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_purchases")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PO #{self.id} - {self.vendor.name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_packages = models.PositiveIntegerField(default=1)
    unit_purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity_packages * self.unit_purchase_price
        super().save(*args, **kwargs)


class SalesOrder(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "Reserved by Client"
        COMPLETED = "COMPLETED", "Completed / Sold"
        CANCELLED = "CANCELLED", "Cancelled"

    client = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_orders"
    )
    processed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="processed_sales"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RESERVED)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SO #{self.id} - {self.status}"


class SalesOrderItem(models.Model):
    class UnitType(models.TextChoices):
        PACKAGE = "PACKAGE", "Full Package"
        SUB_UNIT = "SUB_UNIT", "Sub Unit"

    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit_type = models.CharField(max_length=15, choices=UnitType.choices, default=UnitType.PACKAGE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)