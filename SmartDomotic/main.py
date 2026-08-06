import flet as  ft
import math
class SmartDomotic(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page
        self.page.title ="SmartDomotic"
        self.bg_color = "#ffffff"
        self.dark_white = "#e7e6e9"
        self.prey_color = "#a9acb6"
        self.yellow_color = "#ece5d5"
        self.page.bgcolor = self.bg_color

        self.menu = ft.Container(
            width=60,margin=10,
            alignment=ft.alignment.center,
            content= ft.Column(
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                        ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.MAIL, icon_color= ft.Colors.BLACK)
                                     ),
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.MENU_SHARP, icon_color= ft.Colors.BLACK)
                                     ),
                                ft.Divider(height=1, color=self.dark_white),
                                
                                ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.LIGHT_ROUNDED, icon_color= ft.Colors.BLACK)
                                     ),
                                ft.Divider(height=1, color=self.dark_white),

                                ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.MUSIC_NOTE, icon_color= ft.Colors.BLACK)
                                     ),
                                ft.Divider(height=1, color=self.dark_white),

                                ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.THERMOSTAT, icon_color= ft.Colors.BLACK)
                                     ),
                                ft.Divider(height=1, color=self.dark_white),

                                ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.SECURITY_ROUNDED, icon_color= ft.Colors.BLACK)
                                     ),
                            ]
                        ),

                        ft.Column([
                            ft.Container(width=40, height=40, border_radius=10, bgcolor=self.dark_white,
                                     content= ft.IconButton(icon=ft.Icons.CHECK_CIRCLE, icon_color= ft.Colors.BLACK)
                                     ),
                            ft.Image(src="assets/avatar.jpg", width=40, height=40, border_radius=20,)
                        ])
                ]
            )
        )
        self.colum_1 = ft.Column(
            expand=3,
            alignment= ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Stack(
                    expand=True,
                    alignment=ft.alignment.center,
                    controls=[
                        ft.Container(border_radius=15,
                                     expand=True,
                                     content=ft.Image(
                                         src="assets/foto.png",
                                         fit= ft.ImageFit.COVER,
                                         height=1000,
                                         width=1200,
                                     )
                                     )
                    ]
                ),
                ft.Row(
                    expand=True,
                    controls=[
                        ft.Container(expand=True, bgcolor=self.dark_white,
                                     border_radius=15, padding=10,
                                     ),
                        ft.Container(expand=True, bgcolor=self.prey_color,
                                     border_radius=15,padding=10,
                                     )
                    ]
                )
            ]
        )

        self.colum_2 = ft.Column(
            expand=1, spacing=10,
            alignment= ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(expand=True, border_radius=15, padding=10,
                             gradient= ft.LinearGradient(
                                 rotation = math.radians(90),
                                 colors=[ft.Colors.with_opacity(0.5, self.prey_color),
                                         self.dark_white, self.yellow_color]
                             )
                ),
                ft.Container(
                    expand=True, border_radius=15, bgcolor=self.dark_white, padding=10,
                )
            ]
        )

        self.page.add(
            ft.Row(
                expand=True,
                controls=[
                    self.menu,
                    self.colum_1,
                    self.colum_2,
                ]
            )

        )
    

ft.app(target=SmartDomotic)