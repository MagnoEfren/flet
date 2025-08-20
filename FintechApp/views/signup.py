import flet as ft

class SignUp:
    def __init__(self,page: ft.Page):
        self.page = page 
        

    def build(self, route):
        return ft.View(
            "/signup",
            controls=[
                ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/")),
            ]
        )





    