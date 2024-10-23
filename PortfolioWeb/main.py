
import flet as ft

class PortafolioWeb(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.page.padding = 0
        self.page.fonts = { "Starjhol": "../assets/Starjhol.ttf"}    
        self.text_font = "Tahoma"
        self.page.title = "Mi Portafolio"
        self.color_primaria = ft.colors.GREEN_500

        self.build()
    
    def build(self):

        self.cambiar_modo = ft.IconButton(icon= ft.icons.DARK_MODE, bgcolor= self.color_primaria, on_click= self.cambiar_modo_oscuro)

        self.animation_style = ft.animation.Animation(1000, ft.AnimationCurve.EASE_OUT_CUBIC)

        self.frame_inicio = ft.Container(expand= True,
                                         animate_offset= self.animation_style, 
                                         offset=ft.transform.Offset(0,0),
                                        )

        self.frame_servicio =  ft.Container(expand= True, bgcolor="blue",
                                         animate_offset= self.animation_style, 
                                         offset=ft.transform.Offset(-2,0),
                                        )

        self.titulo_resumen = ft.Text("Mi Experiencia", size=30, weight =ft.FontWeight.W_900, color= self.color_primaria)

        self.frame_experiencia = ft.Container(expand=True,
                                              
                                              )

        self.frame_eduacion = ft.Container(expand=True, visible=False,
                                               ) 

        self.frame_habilidades = ft.Container(expand=True, visible=False,
                                               )

        self.frame_resumen =  ft.Container(expand= True,  bgcolor= "green",
                                         animate_offset= self.animation_style, 
                                         offset=ft.transform.Offset(-2,0),
                                        )

        self.frame_contacto =  ft.Container(expand= True,  bgcolor= "red",
                                         animate_offset= self.animation_style, 
                                         offset=ft.transform.Offset(-2,0),
                                         )

        self.content = ft.Column(
            expand=True,
            spacing=2,
            controls=[
                ft.Container(  #Encabezado 
                    padding=20,
                    content= ft.Row(   
                        expand=True,
                        controls=[
                            ft.Container(expand=True, margin=ft.margin.only(left=20),
                                         content= ft.Text(size=20,
                                                          spans=[
                                                              ft.TextSpan("Nom", style= ft.TextStyle(color=ft.colors.GREEN_100, weight= ft.FontWeight.W_900), ),

                                                               ft.TextSpan("bre", style= ft.TextStyle(color=ft.colors.GREEN_400, weight= ft.FontWeight.W_900), ),
                                                                
                                                                ft.TextSpan(".", style= ft.TextStyle(color=ft.colors.GREEN_900, weight= ft.FontWeight.W_900), ),


                                                          ]
                                                          )
                                         ),

                            ft.ResponsiveRow(
                                alignment= ft.MainAxisAlignment.CENTER,
                                spacing=0,
                                expand=True,
                                controls=[
                                    ft.TextButton("Inicio", style=ft.ButtonStyle(color=self.color_primaria), col={"xs":12, "sm":6, "md":3}, on_click=lambda e: self.cambiar_pagina(0)),
                                    ft.TextButton("Servicio", style=ft.ButtonStyle(color=self.color_primaria), col={"xs":12, "sm":6, "md":3}, on_click=lambda e: self.cambiar_pagina(1)),
                                    ft.TextButton("Resumen", style=ft.ButtonStyle(color=self.color_primaria), col={"xs":12, "sm":6, "md":3}, on_click=lambda e: self.cambiar_pagina(2)),
                                    ft.TextButton("Contacto", style=ft.ButtonStyle(color=self.color_primaria), col={"xs":12, "sm":6, "md":3}, on_click=lambda e: self.cambiar_pagina(3)),
                                ]
                            ),
                        
                            ft.Container(width=50,
                                         margin=ft.margin.only(right=20),
                                         content= self.cambiar_modo                                         
                                         )
                        
                        ]
                    )
                ),

                ft.Container(
                    expand=True,
                    content=ft.Stack(
                        controls=[
                            self.frame_inicio,
                            self.frame_servicio,
                            self.frame_resumen,
                            self.frame_contacto,
                        ]
                    )
                ), # Cuerpo



                ft.Container(
                    padding=20,
                    gradient= ft.LinearGradient(colors=[self.color_primaria, ft.colors.TRANSPARENT]),
                    content= ft.Text("Copyright 2024 Nombre Apellido -  Todos los derechos recervados", size=14)
                ), #parte inferior 
            ]
        )

        self.page.add(self.content)
    
    def cambiar_pagina(self, e):
        self.frame_inicio.offset.x = -2
        self.frame_servicio.offset.x = -2 
        self.frame_resumen.offset.x = -2
        self.frame_contacto.offset.x = -2 

        if e==0:
            self.frame_inicio.offset.x = 0
        if e==1:
            self.frame_servicio.offset.x = 0
        if e==2:
            self.frame_resumen.offset.x = 0
        if e==3:
            self.frame_contacto.offset.x = 0

        self.page.update()

    def cambiar_modo_oscuro(self, e):
        if e.control.icon =="dark_mode":
            self.cambiar_modo.icon = ft.icons.LIGHT_MODE
            self.page.theme_mode = "light"
        else:
            self.cambiar_modo.icon = ft.icons.DARK_MODE
            self.page.theme_mode = "dark"   
        self.page.update()        

    def cambiar_pagina_resumen(self, e):
        self.frame_experiencia.visible = False
        self.frame_eduacion.visible  = False
        self.frame_habilidades.visible  = False

        if e==0:
            self.frame_experiencia.visible = True
            self.titulo_resumen.value = "Mi Experiencia"
        elif e==1:
            self.frame_eduacion.visible = True
            self.titulo_resumen.value = "Mi Educación"
        elif e==2:
            self.frame_habilidades.visible = True
            self.titulo_resumen.value = "Mis Habilidades"

        self.page.update()

ft.app(target=lambda page: PortafolioWeb(page), view= ft.WEB_BROWSER, assets_dir="assets")
