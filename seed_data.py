import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicine.settings')
django.setup()

from pharmacy.models import Category, ActiveIngredient, Product, Vendor, User


def seed_database():
    print("Clearing old catalog data...")
    Product.objects.all().delete()
    Category.objects.all().delete()
    ActiveIngredient.objects.all().delete()
    Vendor.objects.all().delete()

    print("Seeding Vendors...")
    vendor_1 = Vendor.objects.create(
        name="Global Pharma Co.",
        company_name="Global Pharma Distributors",
        phone_number="+100200300",
        email="supply@globalpharma.com",
        address="123 Pharma St, Logistics Hub"
    )

    print("Seeding Categories & Subcategories...")
    parent_meds = Category.objects.create(name="Medicines", description="Pharmaceutical drugs and treatments")
    parent_beauty = Category.objects.create(name="Skincare & Beauty", description="Cosmetics and skin care")

    sub_pain = Category.objects.create(name="Pain Relievers", parent=parent_meds)
    sub_anti = Category.objects.create(name="Antibiotics", parent=parent_meds)
    sub_face = Category.objects.create(name="Facial Care", parent=parent_beauty)

    print("Seeding Active Ingredients...")
    ing_paracetamol = ActiveIngredient.objects.create(
        name="Paracetamol", 
        description="Analgesic and antipyretic for pain and fever."
    )
    ing_ibuprofen = ActiveIngredient.objects.create(
        name="Ibuprofen", 
        description="Nonsteroidal anti-inflammatory drug (NSAID)."
    )
    ing_amoxicillin = ActiveIngredient.objects.create(
        name="Amoxicillin", 
        description="Broad-spectrum penicillin antibiotic."
    )

    print("Seeding Sample Pharmaceutical Products...")
    sample_medicines = [
        {
            "name": "Panadol Extra 500mg",
            "brand": "Haleon",
            "category": sub_pain,
            "active_ingredient": ing_paracetamol,
            "package_unit": "Box",
            "sub_unit": "Strip",
            "units_per_package": 2,
            "package_price": 6.00,
            "sub_unit_price": 3.00,
            "stock_in_sub_units": 100,  # 50 Boxes
            "requires_prescription": False,
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"
        },
        {
            "name": "Cetamol Fast Relief",
            "brand": "PharmaCorp",
            "category": sub_pain,
            "active_ingredient": ing_paracetamol,
            "package_unit": "Box",
            "sub_unit": "Strip",
            "units_per_package": 3,
            "package_price": 7.50,
            "sub_unit_price": 2.50,
            "stock_in_sub_units": 90,   # 30 Boxes
            "requires_prescription": False,
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"
        },
        {
            "name": "Advil Liqui-Gels",
            "brand": "Pfizer",
            "category": sub_pain,
            "active_ingredient": ing_ibuprofen,
            "package_unit": "Box",
            "sub_unit": "Strip",
            "units_per_package": 2,
            "package_price": 9.00,
            "sub_unit_price": 4.50,
            "stock_in_sub_units": 60,
            "requires_prescription": False,
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"
        },
        {
            "name": "Amoxil 500mg Capsules",
            "brand": "GSK",
            "category": sub_anti,
            "active_ingredient": ing_amoxicillin,
            "package_unit": "Box",
            "sub_unit": "Capsule",
            "units_per_package": 12,
            "package_price": 18.00,
            "sub_unit_price": 1.50,
            "stock_in_sub_units": 120,
            "requires_prescription": True,
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=300"
        }
    ]

    for med in sample_medicines:
        Product.objects.create(**med)

    print("Fetching Beauty products from external API...")
    url = "https://dummyjson.com/products/category/beauty"
    response = requests.get(url)

    if response.status_code == 200:
        products_data = response.json().get('products', [])
        for item in products_data:
            Product.objects.create(
                name=item['title'],
                brand=item.get('brand', 'Generic'),
                category=sub_face,
                description=item.get('description', ''),
                package_unit="Item",
                sub_unit="Piece",
                units_per_package=1,
                package_price=item.get('price', 15.00),
                sub_unit_price=item.get('price', 15.00),
                stock_in_sub_units=item.get('stock', 20),
                image_url=item.get('thumbnail', ''),
                requires_prescription=False
            )

    print("Successfully seeded updated database structure!")


if __name__ == "__main__":
    seed_database()