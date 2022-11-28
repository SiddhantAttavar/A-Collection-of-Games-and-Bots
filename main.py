import pygame

from twentyfortyeight.Game import runGame
from twentyfortyeight.AI import runAI

pygame.init()

brinjal = pygame.font.SysFont('Comic Sans',25)
screen = pygame.display.set_mode((int(13.5*35), 9*35))
clock = pygame.time.Clock()

class Button:
	def __init__(self,text,width,height,pos,elevation):
		#Core attributes 
		self.pressed = False
		self.elevation = elevation
		self.dynamic_elecation = elevation
		self.original_y_pos = pos[1]

		# top rectangle 
		self.top_rect = pygame.Rect(pos,(width,height))
		self.top_color = '#475F77'

		# bottom rectangle 
		self.bottom_rect = pygame.Rect(pos,(width,height))
		self.bottom_color = '#354B5E'
		#text
		self.text_surf = brinjal.render(text,True,'#FFFFFF')
		self.text_rect = self.text_surf.get_rect(center = self.top_rect.center)

	def draw(self):
		# elevation logic 
		self.top_rect.y = self.original_y_pos - self.dynamic_elecation
		self.text_rect.center = self.top_rect.center 

		self.bottom_rect.midtop = self.top_rect.midtop
		self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

		pygame.draw.rect(screen,self.bottom_color, self.bottom_rect,border_radius = 12)
		pygame.draw.rect(screen,self.top_color, self.top_rect,border_radius = 12)
		screen.blit(self.text_surf, self.text_rect)
		self.check_click()

	def check_click(self):
		mouse_pos = pygame.mouse.get_pos()
		if self.top_rect.collidepoint(mouse_pos):
			self.top_color = '#D74B4B'
			if pygame.mouse.get_pressed()[0]:
				self.dynamic_elecation = 0
				self.pressed = True
			else:
				self.dynamic_elecation = self.elevation
				if self.pressed == True:
					self.press()
					self.pressed = False
		else:
			self.dynamic_elecation = self.elevation
			self.top_color = '#475F77'
    
	def press(self):
		print('click')

def on2048PressGame():
	runGame(True)

def on2048PressAI():
	runAI()

def onTicTacToePress():
	from TicTacTerminator import GUI

def onSnekPress():
	from Snake import Snake

def onMazePress():
	pass

def onClickAIPress():
	i = 1
	while True:
		print(i, 'click')
		i += 1

run = True
_2048Game = Button('2048 Game',200,40,(20, 20),5)
_2048AI = Button('2048 AI',200,40,(250, 20),5)
TicTacToe = Button('TicTacToe',200,40,(20, 100),5)
MazeAI = Button('Maze AI',200,40,(250, 100),5)
Snek = Button('Snek',200,40,(20, 180),5)
ClickGame = Button('Cookie clicker',200,40,(20, 260),5)
ClickAI = Button('Cookie clicker AI',200,40,(250, 260),5)
bootons = [_2048Game, _2048AI, TicTacToe, MazeAI, Snek, ClickGame, ClickAI]

_2048Game.press = on2048PressGame
_2048AI.press = on2048PressAI
TicTacToe.press = onTicTacToePress
MazeAI.press = onMazePress
Snek.press = onSnekPress
ClickAI.press = onClickAIPress

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    screen.fill((30, 30, 30))
    for b in bootons: b.draw()
    pygame.display.update()

    clock.tick(60)