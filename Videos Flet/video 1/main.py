import flet as ft 
from flet import  Page
import math


def boton_2(e):
    print("BOTON")
    texto_1.value = "BOTON"
    texto_1.color = "green"
    texto_1.rotate = rotate = math.radians(0)


texto_1 = ft.Text("TEXTTO 1",
                  size=20, 
                  weight= ft.FontWeight.W_500,
                  italic= True,
                  color= "red",
               
                  rotate = math.radians(90)
                  )

texto_2 = ft.Text("TEXTTO 1",
                  size=20, 
                  weight= ft.FontWeight.W_500,
                  italic= True,
                 
                  
                  )


boton_1 = ft.FilledButton(
    content= "ft.Icon(icon=ft.Icons.ABC) ",
    icon= ft.Icons.ENERGY_SAVINGS_LEAF,
    icon_color = "red",
    bgcolor= "white",
    on_click=boton_2,
    opacity = 0.5,
)

boton_2 = ft.OutlinedButton(
    content= "OutlinedButton",
    style = ft.ButtonStyle(bgcolor= "white", color= "black",
                           side= ft.BorderSide(2, color="black")
                           )
)


boton_3= ft.TextButton(content="Text Button",
        icon=ft.Icons.STAR_BORDER,
        icon_color=ft.Colors.BLACK_45,
        style = ft.ButtonStyle(bgcolor= "white", color= "black",
                           side= ft.BorderSide(2, color="black")
                           )
        )

boton_4 = ft.IconButton(icon= ft.Icons.SEND,icon_color= "black" )

boton_5 = ft.FloatingActionButton(
    content=ft.Icon(ft.Icons.ADD)
)


def main(page: Page):
    page.title = "Aplicación"
    page.bgcolor = ft.Colors.CYAN_300
    page.padding = 40


    page.add(ft.Column(
        controls=[
        texto_1,
        texto_2,
        boton_1,
        boton_2,
        boton_3,
        boton_4,
        boton_5
    ],
    spacing=40,
    )
    
    )
    




  

ft.run(main)