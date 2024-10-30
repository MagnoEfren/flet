
import flet as ft 
class CustomButton(ft.Container):
    def __init__(self, text, data, on_click):
        super().__init__(expand=True)
        self.border_radius = 40
        self.width = 2*self.border_radius
        self.height = 2*self.border_radius
        self.bgcolor = "white"
        self.data = data
        self.shadow = [
            ft.BoxShadow(
                offset= ft.Offset(15, 15),
                blur_radius=15,
                color= "#250713",
                blur_style= ft.ShadowBlurStyle.NORMAL,         

            ),               
            ft.BoxShadow(
                offset=ft.Offset(-15,-15),
                blur_radius=15,
                color= "#25d7a3",
                blur_style= ft.ShadowBlurStyle.NORMAL,
            )
        ]

        self.content = ft.Text(value=text, color="black", size =20, weight="bold")
        self.alignment = ft.alignment.center
        self.on_click = on_click

def main(page: ft.Page):
    page.bgcolor = "#21bb8e"
    page.padding = 5
    
    def get_data(e):
        data = e.control.data
        if data =="=":
            try:
                text.value = str(eval(text.value))
            except Exception as e:
                text.value = "ERROR"
        elif data =="C":
            text.value = ""
        elif data =="AC":
            text.value = text.value[:-1] if text.value else text.value
        elif data =="%":
            try:
                text.value = str(float(text.value)/100)
            except ValueError:
                text.value = "ERROR"
        elif data ==".":
            if not text.value or text.value[-1] not in [".", "+", "-", "/", "*"]:
                text.value +=data
        elif data =="±":
            text.value = "-"+text.value if text.value and text.value[0]!="-" else text.value[1:]
        elif data in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "+", "-", "/", "*"]:
            text.value +=data        
        page.update()

    
    text = ft.TextField(read_only=True, border_color="#21bb8e", text_align="right",
                        text_style= ft.TextStyle(size=30, color="black"))

    buttons = ft.Column(
        expand= True,
        spacing= 20,
        controls=[

            ft.Row([
                CustomButton(on_click=get_data, text="1", data ="1"),
                CustomButton(on_click=get_data, text="2", data ="2"),
                CustomButton(on_click=get_data, text="3", data ="3"),
                CustomButton(on_click=get_data, text="4", data ="4"),
            ],
            expand=True,
            spacing=20),
            ft.Row([
                CustomButton(on_click=get_data, text="4", data ="4"),
                CustomButton(on_click=get_data, text="5", data ="5"),
                CustomButton(on_click=get_data, text="6", data ="6"),
                CustomButton(on_click=get_data, text="-", data ="-"),
            ],
            expand=True,
            spacing=20),

            ft.Row([
                CustomButton(on_click=get_data, text="7", data ="7"),
                CustomButton(on_click=get_data, text="8", data ="8"),
                CustomButton(on_click=get_data, text="9", data ="9"),
                CustomButton(on_click=get_data, text="x", data ="*"),
            ],
            expand=True,
            spacing=20),

            ft.Row([

                CustomButton(on_click= get_data, text= ".", data="."),
                CustomButton(on_click= get_data, text= "0", data="0"),
                CustomButton(on_click= get_data, text= "%", data="%"),
                CustomButton(on_click= get_data, text= "÷", data="/"),
                ],
                spacing=20,  
                expand=True,               
            ),

            ft.Row([
                CustomButton(on_click= get_data, text= "C", data="C"),
                CustomButton(on_click= get_data, text= "⌫", data="AC"),
                CustomButton(on_click= get_data, text= "±", data="±"),
                CustomButton(on_click= get_data, text= "=", data="="),
                ],
                spacing=20,  
                expand=True,                  
            ),

        ],
        
    )

    content = ft.Container(
        expand=True,
        padding= ft.padding.only(top=120, left=10, right =10, bottom =10),
        content= ft.Column(
            expand=True,
            horizontal_alignment= ft.CrossAxisAlignment.CENTER,
            alignment= ft.alignment.center,
            controls=[
                text,
                buttons,
            ]
        )
    )

    page.add(content)

ft.app(target=main)
