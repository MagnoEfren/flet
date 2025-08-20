import flet  as ft
from views.login import LogIn
from views.signup import SignUp

class FintechApp:
    def __init__(self, page):
        self.page = page
        self.page.on_route_change = self.route_change
        

        self.setup_views()     
        self.page.go("/")
        
   


        self.container = ft.Container(expand=True, 
                                 alignment= ft.alignment.center,
                                 padding=15,
                               gradient= ft.LinearGradient(
                                   colors=["#161177", "#0b0c13", "#2a205e"],
                                   begin = ft.alignment.top_center,
                                   end= ft.alignment.bottom_center
                               ) ,

                               content= ft.Column(
                                   alignment= ft.MainAxisAlignment.CENTER,
                                   horizontal_alignment= ft.CrossAxisAlignment.CENTER,
                                   controls=[
                                       ft.Image(src="assets/icon.png", width=200, height=200),

                                        ft.Text("Empieza tu aventura con las criptomonedas", size=20, weight="bold"),

                                        ft.Text("Crea tu cuenta para operar, almacenar y hacer crecer tus activos digitales de forma segura", size=12),

                                       ft.Container(height=40, width=250,
                                                    bgcolor = "#4decef",
                                                    on_click=lambda e: self.page.go("/login"),
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text("Iniciar Sesión", weight="bold", color = "black"), 
                                                    border_radius=15,
                                                    ),

                                        ft.Container(height=40, width=250,
                                                    bgcolor = "#212334",
                                                    on_click=lambda e: self.page.go("/signup"),
                                                    alignment=ft.alignment.center,
                                                    content=ft.Text("Regístrate", weight="bold", color = "white"), 
                                                    border_radius=15,
                                                    ),

                                   ]
                               ) 
                               )

        
    
    def main_view(self, route):
        return ft.View(
            route="/",
            padding = 0,
            controls=[
                self.container
            ]
        )
    
    def route_change(self, route):
        self.page.views.clear()
        self.page.views.append(self.views.get(self.page.route, self.main_view)(route))
        self.page.update()


    def setup_views(self):
        self.views = {
            "/": self.main_view,
            "/login": LogIn(self.page).build,
            "/signup": SignUp(self.page).build
        }


    def page_login(self, e):
        print("LogIn")

    def page_signup(self, e):
        print("SignUp")


def main(page : ft.Page):
    page.padding = 0
    page.title ="FintechApp"
    FintechApp(page)


ft.app(target=main)
