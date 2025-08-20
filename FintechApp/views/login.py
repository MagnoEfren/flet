import flet as ft

class LogIn(ft.Container):
    def __init__(self,page: ft.Page):
        self.page = page 
        

    def build(self, route):
        return ft.View(
            "/login",
            controls=[
                ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/")),
            ]
        )
