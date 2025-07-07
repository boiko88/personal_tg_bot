import requests
from products import PRODUCT_IDS


class WildberriesParser:
    def __init__(self, product_id, dest=-1257786):
        self.product_id = product_id
        self.dest = dest
        self.url = "https://card.wb.ru/cards/v1/detail"
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }

    def get_product_data(self):
        params = {
            "appType": 1,
            "curr": "rub",
            "nm": self.product_id,
            "spp": 30,
            "dest": self.dest
        }
        response = requests.get(self.url, params=params, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: статус {response.status_code}")

        data = response.json()
        products = data.get("data", {}).get("products", [])
        if not products:
            raise ValueError(f"Продукт с ID {self.product_id} не найден или нет данных.")

        return products[0]

    def parse(self):
        product = self.get_product_data()

        supplier = product.get("supplier")
        if isinstance(supplier, dict):
            supplier_name = supplier.get("name")
        else:
            supplier_name = supplier  # строка или None

            # Получаем URL картинки
        image_url = None
        # Попробуем из sizes:
        sizes = product.get("sizes")
        if sizes and isinstance(sizes, list) and len(sizes) > 0:
            image_url = sizes[0].get("url")
        # Если нет, попробуем из images:
        if not image_url:
            images = product.get("images")
            if images and isinstance(images, list) and len(images) > 0:
                image_url = images[0]

        info = {
            "Название": product.get("name"),
            "Бренд": product.get("brand"),
            "Артикул": product.get("id"),
            "Цена, руб": product.get("salePriceU", 0) / 100,
            "Розничная цена, руб": product.get("retailPriceU", 0) / 100,
            "Остаток": product.get("totalQuantity"),
            "Рейтинг": product.get("rating"),
            "Отзывы": product.get("feedbacks"),
            "Поставщик": supplier_name,
            "Цвет": product.get("colors")[0].get("name") if product.get("colors") else None,
            "Картинка": image_url
        }
        return info


if __name__ == "__main__":
    for product_id in PRODUCT_IDS:
        print(f"\n==== Товар {product_id} ====")
        try:
            parser = WildberriesParser(product_id)
            product_info = parser.parse()
            for key, value in product_info.items():
                print(f"{key}: {value}")
        except Exception as e:
            print(f"Ошибка при обработке ID {product_id}: {e}")
