import flet as ft

class SpendingApp(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(expand=True)
        self.page = page 
        self.bg_color = "#30304d"
        self.page.bgcolor = self.bg_color
        self.blue_color = "#88ddfb"
        self.container_color = "#23243d"
        self.container2_color = "#484a66"

        self.header = ft.Container(
            height=50,
            content=ft.Row(
           alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                    ft.IconButton(icon=ft.icons.ARROW_BACK_IOS, icon_color="white"),
                    ft.Dropdown(
                        width=150,
                        hint_text="Este mes",
                        border_color= self.container2_color,
                        suffix_icon= ft.icons.KEYBOARD_ARROW_DOWN,
                        bgcolor = self.bg_color,
                        border_radius=10,                
                        icon_enabled_color="transparent",
                        options=[
                            ft.dropdown.Option("Noviembre"),
                            ft.dropdown.Option("Diciembre"),
                            ft.dropdown.Option("Enero"),
                        ],
                    ),
                    ft.Image(src= "assets/avatar.png", height=40, width=40, border_radius=20 )
            ]
        )
        )
        self.title = ft.Container(
            height=20, padding=0,
            content=ft.Text("2 de enero, 2025 al 15 de enero 2025.", color=ft.colors.with_opacity(0.5, "white"))
            )
        
        self.row_1 = ft.Container(
            content=ft.Row([
                ft.Container(
                    height=80,
                    expand=True,padding=5,
                    bgcolor=self.container2_color,
                    border_radius=10,
                    content=ft.Column(
                        controls=[
                            ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Ingreso"),
                            ft.Container(
                                alignment=ft.alignment.center,
                                bgcolor="green",
                                height=10, width=10,
                                border_radius=5
                            )
                        ]
                    ),
                    ft.Text("$ 74,900", size=25, weight="bold"),
                    ]
                    )
                ),
                ft.Container(
                    height=80,
                    expand=True,padding=5,
                    bgcolor=self.container2_color,
                    border_radius=10,
                    content=ft.Column(
                        controls=[
                            ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text("Gastos"),
                            ft.Container(
                                alignment=ft.alignment.center,
                                bgcolor="red",
                                height=10, width=10,
                                border_radius=5
                            )
                        ]
                    ),
                    ft.Text("$ 24,845", size=25, weight="bold"),
                    ]
                    )
                )
            ])
        )

        ##grafica
        x_values = list(range(1, 16))
        green_line = [1.2, 1.5, 2.0, 8, 3.2, 5, 2.0, 2.5, 5, 10, 2.1, 4, 2.0, 6, 1.7]
        red_line = [1.8, 8, 1.5, 7, 1.6, 1.8, 2.0, 10, 1.8, 3, 2.0, 2.2, 5, 2.0, 9]

        bottom_axis = ft.ChartAxis(labels_size=25, labels_interval=3, show_labels=True)
        left_axis = ft.ChartAxis(labels_size=25, labels_interval=5, show_labels=True)

        self.chart_data = ft.LineChart(
            tooltip_bgcolor="transparent",
            data_series=[
                ft.LineChartData(
                    data_points=[ft.LineChartDataPoint(x, y, selected=(x == 8)) for x, y in zip(x_values, green_line)],
                    color=ft.colors.GREEN,
                    stroke_width=1,
                    curved=True,
                    below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.GREEN),
                ),
                ft.LineChartData(
                    data_points=[ft.LineChartDataPoint(x, y, selected=(x == 8)) for x, y in zip(x_values, red_line)],
                    color=ft.colors.RED,
                    stroke_width=1,
                    curved=True,
                    below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.RED),
                )
            ],
            min_y=0,
            max_y=10,
            expand=True,
            border=ft.Border(
                bottom=ft.BorderSide(1, ft.colors.with_opacity(0.3, ft.colors.WHITE)),
                left=ft.BorderSide(1, ft.colors.with_opacity(0.3, ft.colors.WHITE))
            ),
            bottom_axis=bottom_axis,
            left_axis=left_axis,
        )

        self.row_2 = ft.Container(
            bgcolor= self.container2_color,
            border_radius=10,
            height=120,padding=10,
            content=ft.Column(
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Diferencia"),
                                    ft.Text("$ 18,290", size=15, weight="bold"),
                                ]
                            ),
                            # grafica
                            self.chart_data
                        ]
                )
        )

        self.row_3 = ft.Container(
            height=30,
            border_radius=10,
            bgcolor=self.container_color,
            content=ft.Row(
                alignment= ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                ft.ElevatedButton(text="Todos", color=self.container2_color, bgcolor=self.container_color,
                                style = ft.ButtonStyle(side = ft.BorderSide(1, self.container2_color),
                                        shape=ft.RoundedRectangleBorder(radius=10) 
                                )                                
                                ),
                ft.ElevatedButton(text="Ingresos",color=self.container2_color, bgcolor=self.container_color,
                                style = ft.ButtonStyle(side = ft.BorderSide(1, self.container2_color),
                                        shape=ft.RoundedRectangleBorder(radius=10)                                 
                                )
                                ),
                ft.ElevatedButton(text="Gastos", bgcolor=self.container2_color, color="white",
                                style = ft.ButtonStyle(side = ft.BorderSide(1, self.container2_color),
                                        shape=ft.RoundedRectangleBorder(radius=10)                                 
                                )
                                ),
            ])
        )

        self.row_4 = ft.Container(
            bgcolor=self.container_color,
            height=120,padding=5,
            border_radius=10,   
            border=ft.border.all(1, self.container2_color),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(icon=ft.icons.DIRECTIONS_CAR_FILLED_OUTLINED, icon_color="white"),
                            ft.Text("Viajes y Transporte", color=self.container2_color),
                            ft.IconButton(icon=ft.icons.EDIT_CALENDAR, icon_color="white"),
                        ]
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([
                                ft.Text("Vuelo", color=self.container2_color, width=40),
                                ft.ProgressBar(value=0.7, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("70 %", color=self.container2_color),
                            ]),
                            ft.Row([
                                ft.Text("Tren", color=self.container2_color, width=40),
                                ft.ProgressBar(value=0.85, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("85 %", color=self.container2_color),
                            ]),
                            ft.Row([
                                ft.Text("Taxi", color=self.container2_color, width=40),
                                ft.ProgressBar(value=0.65, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("68 %", color=self.container2_color),
                            ]),
                           
                        ]
                    ),
                ]
            )
        )
        self.row_5 = ft.Container(
            bgcolor=self.container_color,
            height=120,padding=5,
            border_radius=10,   
            border=ft.border.all(1, self.container2_color),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.IconButton(icon=ft.icons.HOME_OUTLINED, icon_color="white"),
                            ft.Text("Casa", color=self.container2_color),
                            ft.IconButton(icon=ft.icons.EDIT_CALENDAR, icon_color="white"),
                        ]
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row([
                                ft.Text("Luz", color=self.container2_color, width=60),
                                ft.ProgressBar(value=0.75, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("75 %", color=self.container2_color),
                            ]),
                            ft.Row([
                                ft.Text("Agua", color=self.container2_color, width=60),
                                ft.ProgressBar(value=0.39, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("39 %", color=self.container2_color),
                            ]),
                            ft.Row([
                                ft.Text("Internet", color=self.container2_color, width=60),
                                ft.ProgressBar(value=0.45, bgcolor=self.container2_color, border_radius=5, height=5, width=150,
                                color="white",
                                ),
                                ft.Text("45 %", color=self.container2_color),
                            ]),
                           
                        ]
                    ),
                ]
            )
        )

        self.row_6 = ft.Container(
            bgcolor=self.container_color,
            height=60,padding=10,
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Total gastado $7,800", color=self.container2_color, weight="bold",size=15),
                            ft.ProgressBar(value=0.45, bgcolor=self.container2_color, border_radius=5, height=10, width=150,
                                color=self.blue_color)
                        ]
                    ),
                    ft.IconButton(icon=ft.icons.POWER_SETTINGS_NEW, bgcolor="transparent",
                                style = ft.ButtonStyle(side = ft.BorderSide(1, self.container2_color),
                                        shape=ft.RoundedRectangleBorder(radius=10)                                 
                                )
                                ),
                ]
            )
        )


        self.page.add(ft.Column(
            expand=True, scroll="auto",
            controls=[
                    self.header,
                    self.title,
                    self.row_1,
                    self.row_2,
                    self.row_3,
                    self.row_4,
                    self.row_5,
                    self.row_6
            ]
        ))

ft.app(target=SpendingApp)


