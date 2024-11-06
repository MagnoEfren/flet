#   Primera parte del código
#   ¡Únete como miembro del Nivel 💎💎💎!
#   Accede al código completo de todos los videos, que no estan en github. 


import flet as ft 

class ProductPage(ft.View):
    def __init__(self, page, img_src, title, sub_title, price, rating):
        pass

    def build_view(self):
        pass

    def close_product_page(self, e):
        pass
    
    def add_favorite(self, e):
        print(1)


class ProductCard(ft.Container):  
    def __init__(self,page, img_src, title, sub_title, price, rating):
        pass


    def expandir_contenedor(self, e):
        pass

    def  add_favorites(self, e):
        pass

class AppShopCoffee(ft.Container):
    def __init__(self, page):
        super().__init__()
   
    def filter_products(self, e):
        pass

    def change_position(self, e):
        pass
    
ft.app(target=AppShopCoffee)
