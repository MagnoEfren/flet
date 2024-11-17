# Magno Efren 
# https://www.youtube.com/@MagnoEfren/videos

import flet as ft 
import random 
import time 
import threading 


class MyApp(ft.UserControl):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        self.x = 0

        self.slider1 = ft.Slider( value= 30, min = 0, max = 100,
                                 inactive_color="black", expand= True,
                                 active_color= "white",
                                 on_change= self.value_slider1)

        self.slider2 = ft.Slider( value= 50, min = 0, max = 100,
                                 inactive_color="black", expand= True,
                                 active_color= "white",
                                 on_change= self.value_slider2)
        
        self.slider3 = ft.Slider( value= 20, min = 0, max = 100,
                                 inactive_color="black", expand= True,
                                 active_color= "white",
                                 on_change= self.value_slider3)
        
        self.slider4 = ft.Slider( value= 80, min = 0, max = 100,
                                 inactive_color="black", expand= True,
                                 active_color= "white",
                                 on_change= self.value_slider4)
        

        self.indicator1 = ft.Text(value= "30%", color= "black")
        self.indicator2 = ft.Text(value= "50%", color= "black")
        self.indicator3 = ft.Text(value= "20%", color= "black")
        self.indicator4 = ft.Text(value= "80%", color= "black")    



        self.control1 = ft.Row([self.slider1, self.indicator1], spacing= 0, expand=True)
        self.control2 = ft.Row([self.slider2, self.indicator2], spacing= 0, expand=True)
        self.control3 = ft.Row([self.slider3, self.indicator3], spacing= 0, expand=True)
        self.control4 = ft.Row([self.slider4, self.indicator4], spacing= 0, expand=True)



        self.data1 = [ft.LineChartData(data_points=[],
                                       curved=True,
                                       stroke_width=2,
                                       color  = "black",
                                       point= True,
                                       )]
        

        self.graph1 = ft.LineChart(data_series= self.data1,
                                   min_x= 0,
                                   max_x= 50,
                                   max_y= 50,
                                   min_y= 0,
                                   point_line_start=0,
                                   expand=True,
                                   interactive= False,
                                   left_axis= ft.ChartAxis(visible= True,
                                                           labels_size= 30,),

                                   bottom_axis= ft.ChartAxis(visible= True,
                                                           labels_size= 30,),
                                   border= ft.Border(
                                       bottom= ft.BorderSide(2,
                                                             ft.colors.with_opacity(0.3,
                                                                                    "white")),
                                       left= ft.BorderSide(2,
                                                             ft.colors.with_opacity(0.3,
                                                                                    "white")),
                                   ),
                                   )
        


        self.data2 = [ ft.LineChartData(data_points= [ft.LineChartDataPoint(0, int(self.slider1.value)),
                                                      ft.LineChartDataPoint(25, int(self.slider2.value)),
                                                      ft.LineChartDataPoint(50, int(self.slider3.value)),
                                                      ft.LineChartDataPoint(100, int(self.slider4.value)),
                                                      ],
                                        curved= True,
                                        stroke_width=2,
                                        color = "black",
                                        point = True,
                                        below_line_gradient= ft.LinearGradient(["white", "purple"]) 
                                                      )]





        self.graph2 = ft.LineChart( data_series= self.data2,
                                   min_x=0,
                                   max_x= 100,
                                   min_y=0,
                                   max_y= 100,
                                   point_line_start=0,
                                   expand=True,
                                   interactive= False,
                                   border= ft.Border(
                                       bottom= ft.BorderSide(2,
                                                             ft.colors.with_opacity(0.3,
                                                                                    "white")),
                                       left= ft.BorderSide(2,
                                                             ft.colors.with_opacity(0.3,
                                                                                    "white")),

                                   ),
                                   )


        self.threading = threading.Thread( target= self.real_time_data)
        self.threading.start()


        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    gradient= ft.LinearGradient(["purple", "white"], rotation=30),
                    border_radius=10,
                    content= ft.Column(
                        alignment= ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                height=60,
                                padding=10,
                                alignment= ft.alignment.center,
                                content= ft.Text("Gráfica en tiempo real",
                                                 color = "black",
                                                 font_family="vivaldi",
                                                 size=30,
                                                 weight="bold")
                            ),
                        
                        ft.Container(
                            expand=True,
                            content= self.graph1,
                            padding= 20,
                        )
                        ]
                    )
                ),


                ft.Container(
                    gradient= ft.LinearGradient(["purple", "white"]),
                    expand=True,
                    border_radius= 10,
                    padding=10,
                    content= ft.Row(
                        spacing=20,
                        controls=[
                            ft.Column(
                                expand=True,
                                controls= [
                                    self.control1,
                                    self.control2,
                                    self.control3,
                                    self.control4,
                                ]
                            ),

                            ft.Column(
                                expand=True,
                                controls=[
                                    self.graph2
                                ]
                            )
                        ]
                    )
                ),
            ]
        )
    def build(self):
        return self.content 
    

    def value_slider1(self, e):
        self.indicator1.value = str(f"{int(self.slider1.value)} %")
        self.data2[0].data_points[0].y = self.slider1.value
        self.update()
        
    def value_slider2(self, e):
        self.indicator2.value = str(f"{int(self.slider2.value)} %")
        self.data2[0].data_points[1].y = self.slider2.value
        self.update()
        
    def value_slider3(self, e):
        self.indicator3.value = str(f"{int(self.slider3.value)} %")
        self.data2[0].data_points[2].y = self.slider3.value
        self.update()

    def value_slider4(self, e):
        self.indicator4.value = str(f"{int(self.slider4.value)} %")
        self.data2[0].data_points[3].y = self.slider4.value
        self.update()


    def real_time_data(self):
        while True:
            self.x  += 1
            data = random.randint(5, 45)
            self.data1[0].data_points.append(ft.LineChartDataPoint(self.x, data))

            if len(self.data1[0].data_points) ==50:
                self.x = 0
                self.data1[0].data_points.clear()
            self.update()
            time.sleep(0.3)

def main(page: ft.Page):
    page.add(MyApp(page))

ft.app(target=main)
