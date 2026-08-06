
#   Primera parte del código
#   ¡Únete como miembro del Nivel 💎💎💎!
#   Accede al código completo de todos los videos, que no estan en github. 

import flet as ft 

class AppShopCoffee(ft.Container):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.color_caffee = "#b9894b"
        self.bg_color = "#0c0f14"
        self.container_color = "#141821"
        self.nav_color = "#18191b"
        self.page.spacing = 5
        self.page.paddong = 5
        self.page.bgcolor = self.bg_color
        self.page.fonts = {"Poppins": "Poppins-Regular.ttf"}
        self.page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thumb_color=self.color_caffee),font_family="Poppins")
        
        self.container_1 = ft.Container(expand=True,
                padding=10,
                offset=ft.transform.Offset(0, 0),
                content=ft.Column(expand=True,
                                 controls=[
                                     ft.Row(alignment= ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.IconButton(icon=ft.Icons.MENU, icon_color="white"),
                                                ft.Container(ft.Image(src="assets/images/avatar.jpg", height=30,), border_radius=10)
                                            ])
                                 ]
                                 )

        )

        self.page.add(
            ft.Column(expand=True,
                      controls=[
                          ft.Stack(
                              expand=True,
                              controls=[
                                  self.container_1,
                              ]
                          ),
                          ft.Stack(
                              height=60,
                              controls=[
                                  
                              ]
                          )
                      ]

            )
        )
    
    
ft.app(target=AppShopCoffee)
