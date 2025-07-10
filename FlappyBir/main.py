import flet as ft 
import random
import asyncio

# configuracion del juego 
GAME_WIDTH = 288
GAME_HEIGHT = 512
GRAVITY = 0.5
FLAP_STRENGTH = -8 
PIPE_GAP = 150
PIPE_SPEED = 2


class FlappyBirdGame(ft.Container):
    def __init__(self, page):
        super().__init__(expand=True)
        self.page = page 
        self.bird_y = GAME_HEIGHT//2 
        self.bird_velocity = 0
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.alignment = ft.alignment.center


        self.sound_hit = ft.Audio(src="assets/audios/hit.wav", autoplay=False)
        self.sound_point = ft.Audio(src="assets/audios/point.wav", autoplay=False)
        self.sound_wing = ft.Audio(src="assets/audios/wing.wav", autoplay=False)
        

        self.background_img = ft.Image(src="assets/images/background.png", width=GAME_WIDTH, height=GAME_HEIGHT)

        self.bird_images = [
            "assets/images/redbird-midflap.png",
            "assets/images/redbird-downflap.png",
            "assets/images/redbird-upflap.png",
        ]

        self.bird_frame = 0
        self.bird_img = ft.Image(src= self.bird_images[self.bird_frame], width=34, height=24, left=50, top=self.bird_y)

        self.pipe_img_top = ft.Image(src="assets/images/pipe-green.png", width=52, height=320, rotate=ft.Rotate(angle=3.13159))

        self.pipe_img_bottom = ft.Image(src="assets/images/pipe-green.png", width=52, height=320)

        self.floor_img = ft.Image(src="assets/images/floor.png", width=GAME_WIDTH, height=112, top=GAME_HEIGHT-112)

        self.game_over_img = ft.Image(src="assets/images/gameover.png", width=192, height=42,
                                      left=GAME_WIDTH//2 -96, top=GAME_HEIGHT//2-21, visible=False,
                                      )

        self.message_img = ft.Image(src="assets/images/message.png", width=184, height=267,
                                      left=GAME_WIDTH//2 -92, top=GAME_HEIGHT//2-133, visible=True,
                                      )
               
        self.score_images = []


        self.stack = ft.Stack([
            self.background_img,
            self.pipe_img_top,
            self.pipe_img_bottom,
            self.bird_img,
            self.floor_img,
            *self.score_images,
            self.game_over_img,
            self.message_img,
            self.sound_hit,
            self.sound_point,
            self.sound_wing
            
        ],
        width= GAME_WIDTH,
        height= GAME_HEIGHT
        )
        self.update_score_display()

        self.content = self.stack

    def generate_pipe(self):
        pipe_height = random.randint(100, 300)
        return {"x": GAME_WIDTH, "y_top": pipe_height-320, "y_bottom": pipe_height+PIPE_GAP}
    
    def update_score_display(self):
        score_str = str(self.score)
        self.score_images.clear()
        total_width = len(score_str)*24
        start_x = (GAME_WIDTH-total_width)//2
        for i, digit in enumerate(score_str):
            self.score_images.append(ft.Image(
                src=f"assets/images/{digit}.png", width=24, height=36,left=start_x+i*24, top=50
            ))
        
        self.stack.controls = [
            self.background_img,
            self.pipe_img_top,
            self.pipe_img_bottom,
            self.bird_img,
            self.floor_img,
            *self.score_images,
            self.game_over_img,
            self.message_img,
            self.sound_hit,
            self.sound_point,
            self.sound_wing
        ]

        self.update()
    
    def move(self):
        if self.game_over  or not self.game_started:
            return
        self.bird_velocity+=GRAVITY
        self.bird_y+= self.bird_velocity
        self.bird_img.top = self.bird_y

        for pipe in self.pipes:
            pipe["x"] -=PIPE_SPEED
        if len(self.pipes)==0 or self.pipes[-1]["x"] < GAME_WIDTH-200:
            self.pipes.append(self.generate_pipe())
        
        if len(self.pipes)>0 and self.pipes[0]["x"] <-52:
            self.pipes.pop(0)
            self.score+=1
            self.sound_point.play()
            self.update_score_display()

        for pipe in self.pipes:
            if (50<pipe["x"]<84) and (self.bird_y < pipe["y_top"]+320 or self.bird_y+ 24> pipe["y_bottom"]):
                self.game_over = True
                self.game_over_img.visible = True
                self.sound_hit.play()

        if self.bird_y> GAME_HEIGHT -112:
            self.game_over = True
            self.game_over_img.visible = True
            self.sound_hit.play()

        if len(self.pipes)>0:
            self.pipe_img_top.left = self.pipes[0]["x"]
            self.pipe_img_top.top = self.pipes[0]["y_top"]
            self.pipe_img_bottom.left = self.pipes[0]["x"]
            self.pipe_img_bottom.top = self.pipes[0]["y_bottom"]
        self.animate_bird()
        self.update()

    
    def on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == " ":
            if not self.game_started:
                self.game_started  = True
                self.message_img.visible = False
            if not self.game_over:
                self.bird_velocity = FLAP_STRENGTH
                self.sound_wing.play()
        elif e.key =="Enter" and self.game_over:
            self.reset()

    def animate_bird(self):
        self.bird_frame = (self.bird_frame+1)%(len(self.bird_images))
        self.bird_img.src = self.bird_images[self.bird_frame]
        self.bird_img.update()

    def reset(self):
        self.bird_y = GAME_HEIGHT//2 
        self.bird_velocity = 0
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.message_img.visible = True           
        self.update_score_display()
        self.game_over_img.visible = False
        self.update()

    def update(self):
        self.page.update()


async def game_loop(game):
    while True:
        if not game.game_over  and game.game_started:
            game.move()
        game.page.update()
        await asyncio.sleep(0.02)

async def main(page: ft.Page):
    page.title= "Flappy Bird"
    page.window.width = GAME_WIDTH + 40
    page.window.height = GAME_HEIGHT + 40
    page.window.resizable = False
    page.bgcolor = ft.Colors.BLACK

    game = FlappyBirdGame(page)
    page.on_keyboard_event  = game.on_keyboard
    page.add(ft.Stack(alignment=ft.alignment.center, controls=[game]))
    asyncio.create_task(game_loop(game))



ft.app(target= main)