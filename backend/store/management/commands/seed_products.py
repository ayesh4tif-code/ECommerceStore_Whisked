from decimal import Decimal

from django.core.management.base import BaseCommand

from store.models import Product


PRODUCTS = [
    {
        "id": 1,
        "title": "The Choco-Loop",
        "category": "Cookies",
        "price": "12.00",
        "rating": "4.8",
        "reviews": 142,
        "image": "https://i.pinimg.com/736x/56/2a/79/562a790101b30a174447a8e8554c5f05.jpg",
        "hover_image": "https://i.pinimg.com/736x/d4/93/68/d49368aa3f88bde09e2f8e995028c10b.jpg",
        "cart_image": "https://i.pinimg.com/736x/1a/07/c8/1a07c88547581f3de4222a454071fc51.jpg",
        "description": "A delicious spin on the classic chocolate chip cookie. Its unique ring shape delivers maximum crispy edges with every bite.",
        "specs": ["100% Organic Cacao", "Batch of 6", "Gluten-Free Option"],
    },
    {
        "id": 2,
        "title": "Cloud Vanilla Bean Chiffon Cake",
        "category": "Cakes",
        "price": "28.50",
        "rating": "4.9",
        "reviews": 89,
        "image": "https://i.pinimg.com/736x/9c/19/c8/9c19c823bfbae2ceefb0fa0743200e42.jpg",
        "hover_image": "https://i.pinimg.com/736x/36/c0/7d/36c07d3db701d501a809cf981f7fadad.jpg",
        "cart_image": "https://i.pinimg.com/736x/de/82/65/de8265380affd58acfd6b7f28e29edad.jpg",
        "description": "A whisper-light sponge infused with real vanilla bean. Served with fresh raspberries and organic whipped cream on the side.",
        "specs": ["Real Madagascar Vanilla", "6-inch Round", "Low Sugar"],
    },
    {
        "id": 3,
        "title": "Choco Mousse Extravaganza",
        "category": "Cakes",
        "price": "34.00",
        "rating": "4.7",
        "reviews": 215,
        "image": "https://i.pinimg.com/736x/49/d4/f4/49d4f4c7a34717098591ddf81b4a2dcb.jpg",
        "hover_image": "https://i.pinimg.com/736x/aa/03/3f/aa033f6ced32159ee44f6460e36cdf90.jpg",
        "cart_image": "https://i.pinimg.com/736x/f2/35/51/f235517a0641506571b65038a290f86b.jpg",
        "description": "Velvety dark chocolate mousse resting on a whisper-soft sponge. Crowned with a glossy fudge drip and crisp chocolate shards.",
        "specs": ["70% Belgian Chocolate", "Serves 8-10", "Contains Nuts"],
    },
    {
        "id": 4,
        "title": "The Strawberry Glazed Donut",
        "category": "Pastries",
        "price": "4.25",
        "rating": "4.6",
        "reviews": 310,
        "image": "https://images.unsplash.com/photo-1533910534207-90f31029a78e?w=800&auto=format&fit=crop&q=80",
        "hover_image": "https://i.pinimg.com/736x/30/3a/a1/303aa1b98bb4c274b87cd3157e6ad5a3.jpg",
        "cart_image": "https://i.pinimg.com/736x/df/a7/99/dfa799314fb003c983514177f24c859c.jpg",
        "description": "A soft, golden yeast ring dipped in a sweet strawberry glaze and finished with a classic sprinkle crunch.",
        "specs": ["Fresh Farm Strawberries", "Artisanal Brioche", "Nut-Free"],
    },
    {
        "id": 5,
        "title": "Artisanal Butter Croissant",
        "category": "Pastries",
        "price": "4.50",
        "rating": "4.9",
        "reviews": 520,
        "image": "https://i.pinimg.com/736x/a2/06/1c/a2061c510ffcf9380df5de20234a3630.jpg",
        "hover_image": "https://i.pinimg.com/736x/bb/a0/35/bba035080c43d65b383de08890cc78d2.jpg",
        "cart_image": "https://i.pinimg.com/736x/5f/3b/18/5f3b18b58f24a44d94bce028a7ef2bb2.jpg",
        "description": "A golden, flaky 72-hour laminated French butter croissant baked fresh daily, finished with a bespoke cocoa drizzle.",
        "specs": ["Pure French Butter", "72-Hour Ferment", "Fresh Daily"],
    },
    {
        "id": 6,
        "title": "Red Velvet & Cream",
        "category": "Cupcakes",
        "price": "5.50",
        "rating": "4.8",
        "reviews": 176,
        "image": "https://i.pinimg.com/736x/92/78/e7/9278e7937f86ac9e83f36dd45afd9bb5.jpg",
        "hover_image": "https://i.pinimg.com/736x/b9/a4/4b/b9a44b0671b7ac480d121fb96667a972.jpg",
        "cart_image": "https://i.pinimg.com/736x/1f/4b/f0/1f4bf08db230e5dd7e582ec72562fbab.jpg",
        "description": "A tender, cocoa-rich cupcake topped with a generous swoop of house-made frosting, tart berries, and cake crumbs.",
        "specs": ["Cream Cheese Frosting", "Single Portion", "Eggless Option"],
    },
]


class Command(BaseCommand):
    help = "Create or update the Whisked storefront products."

    def handle(self, *args, **options):
        for product in PRODUCTS:
            values = {key: value for key, value in product.items() if key != "id"}
            values["price"] = Decimal(values["price"])
            Product.objects.update_or_create(pk=product["id"], defaults=values)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(PRODUCTS)} products."))
