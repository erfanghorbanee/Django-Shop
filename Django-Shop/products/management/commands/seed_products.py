from random import choice, randint

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from model_bakery import baker
from products.models import Category, Product, ProductImage

fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with fake categories, subcategories, products, and product images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--products", type=int, default=50, help="Total number of products"
        )
        parser.add_argument("--images", type=int, default=2, help="Images per product")

    def handle(self, *args, **options):
        num_products = options["products"]
        num_images = options["images"]

        # Standard e-commerce categories and subcategories
        category_structure = {
            "Electronics": ["Laptops", "Smartphones", "Headphones", "Cameras"],
            "Clothing": ["Men's Clothing", "Women's Clothing", "Shoes", "Accessories"],
            "Home & Kitchen": ["Furniture", "Appliances", "Cookware", "Decor"],
            "Sports & Outdoors": ["Fitness", "Cycling", "Camping", "Footwear"],
            "Beauty": ["Skincare", "Makeup", "Hair Care", "Fragrances"],
            "Toys & Games": ["Board Games", "Puzzles", "Outdoor Play", "Educational"],
            "Books": ["Fiction", "Non-Fiction", "Children's Books", "Comics"],
            "Automotive": [
                "Car Electronics",
                "Tools",
                "Accessories",
                "Motorcycle Parts",
            ],
        }

        self.stdout.write(self.style.SUCCESS("Deleting old data..."))
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(
            self.style.SUCCESS("Creating categories and subcategories...")
        )
        parent_categories = {}
        all_categories = []
        used_names = set()
        for parent_name, subcats in category_structure.items():
            if parent_name in used_names:
                continue
            parent = baker.make(Category, name=parent_name, parent=None)
            parent_categories[parent_name] = parent
            all_categories.append(parent)
            used_names.add(parent_name)
            for subcat_name in subcats:
                if subcat_name in used_names:
                    continue
                subcat = baker.make(Category, name=subcat_name, parent=parent)
                all_categories.append(subcat)
                used_names.add(subcat_name)

        # Product name and image keywords by category
        product_keywords = {
            "Electronics": ["laptop", "smartphone", "headphones", "camera"],
            "Clothing": ["shirt", "dress", "shoes", "jacket"],
            "Home & Kitchen": ["sofa", "blender", "pan", "lamp"],
            "Sports & Outdoors": ["bicycle", "tent", "dumbbell", "sneakers"],
            "Beauty": ["cream", "lipstick", "shampoo", "perfume"],
            "Toys & Games": ["board game", "puzzle", "swing", "lego"],
            "Books": ["novel", "biography", "storybook", "comic"],
            "Automotive": ["car stereo", "wrench", "seat cover", "helmet"],
        }

        self.stdout.write(self.style.SUCCESS("Creating products..."))
        products = []
        for _ in range(num_products):
            category = choice(all_categories)
            # Find the top-level category for image/keyword
            parent = category.parent if category.parent else category
            parent_name = parent.name
            keyword = choice(product_keywords.get(parent_name, ["product"]))
            # Generate a realistic product name
            product_name = fake.unique.catch_phrase() + f" {keyword.title()}"
            description = fake.sentence(nb_words=12) + " " + fake.text(max_nb_chars=120)
            price = round(
                fake.pydecimal(left_digits=2, right_digits=2, positive=True), 2
            )
            discount_percent = randint(0, 50)
            stock = randint(0, 100)
            is_available = choice([True, True, True, False])
            product = baker.make(
                Product,
                name=product_name,
                description=description,
                price=price,
                discount_percent=discount_percent,
                stock=stock,
                is_available=is_available,
                category=category,
            )
            products.append((product, keyword))

        self.stdout.write(self.style.SUCCESS("Adding images to products..."))
        for product, keyword in products:
            for _ in range(num_images):
                url = "https://picsum.photos/400/400"
                self.stdout.write(f"Fetching image for {product.name} from {url}")
                try:
                    resp = requests.get(url, timeout=10)
                    self.stdout.write(
                        f"Status code: {resp.status_code}, Content-Type: {resp.headers.get('Content-Type')}"
                    )
                    if resp.status_code == 200 and resp.headers.get(
                        "Content-Type", ""
                    ).startswith("image/"):
                        image_file = ContentFile(
                            resp.content, name=fake.file_name(extension="jpg")
                        )
                        ProductImage.objects.create(product=product, image=image_file)
                        self.stdout.write(
                            self.style.SUCCESS(f"Image saved for {product.name}")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"No image saved for {product.name} (bad response)"
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Failed to fetch image for {product.name}: {e}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
