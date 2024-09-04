# @autor: Magno Efren
# Youtube: https://www.youtube.com/c/MagnoEfren

import flet as ft 
import cv2
import base64
import threading
import time 

class CameraApp(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page
        self.page.window_width = 900
        self.frame = None
        self.thread_running = True

        self.page.window_prevent_close = True
        self.page.on_window_event = self.window_event

        self.capture = cv2.VideoCapture(1)
        if not self.capture.isOpened():
            raise ValueError("No se logro conectar a la cámara")

        path = base64.b64encode(open("camara.png", "rb").read()).decode("utf-8")
        self.video1 = ft.Image(src_base64=path,  expand=True)
        self.video2 = ft.Image(src_base64=path,  expand=True)


        self.confirm_dialog = ft.AlertDialog(
            modal= True,
            title= ft.Text("Por favor confirme"),
            content= ft.Text("¿Está seguro de que desea salir de la aplicación?"),
            actions=[
                ft.ElevatedButton("SI", on_click= self.yes_click),
                ft.OutlinedButton("NO", on_click= self.no_click)
            ]
        )


        self.cameras = ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    border_radius=10,
                    content= self.video1
                ),
                ft.Container(
                    expand=True,
                    border_radius=10,
                    content= self.video2
                ),
            ]
        )

        self.info_text = ft.Column(
            expand=True,
            controls=[
                ft.Container(
                    expand=True,
                    border_radius=10,
                    bgcolor="blue"
                ),
                ft.Container(
                    expand=True,
                    border_radius=10,
                    bgcolor="blue"
                ),
            ]
        )


        self.page.add(ft.Row(
            expand=True,
            controls=[
                self.cameras,
                self.info_text
            ]
        ))
    
        self.threading = threading.Thread(target = self.update_frame_camera)
        self.threading.start()
    
    def update_frame_camera(self):
        while self.thread_running:
            ret, frame = self.capture.read()
            if ret:
                _, buffer = cv2.imencode(".png", frame)
                self.frame =  base64.b64encode(buffer).decode("utf-8")
                self.video1.src_base64 = self.frame
                self.video2.src_base64 = self.frame
                self.page.update()
            else:
                print("Error al capturar el video")
            time.sleep(0.03)

    
    def window_event(self, e):
        if e.data =="close":
            self.page.overlay.append(self.confirm_dialog)
            self.confirm_dialog.open = True
            self.page.update()
    

    def yes_click(self, e):
        self.thread_running = False
        if self.threading.is_alive():
            self.threading.join()
        self.capture.release()    
        self.page.window_close()
        self.page.window_destroy()
    
    def no_click(self, e):
        self.confirm_dialog.open = False
        self.page.update()



ft.app(target= CameraApp)
