"""
Path Finding using A* Algorithm
Maze Generation using Depth First Search

Heuristics:
Euclidean Distance by default
Manhattan Distance if maze is generated

ticks control speed of animation of maze generation and path finding (higher number = slower)

- First click places a cell that determines start position
- Second click places end cell
- Any cell placed after that indicates a wall
- Right click to delete cells
"""

import pygame
pygame.init()
import random as rnd

rand_col = lambda: (rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255))
FPS = 144
deg = 6  # Increase window size by increasing deg (window size ~ 2^deg)
grid_size = 2**deg+1

ticks = 1   # How fast the simulation runs
maze_senstivity = 1  # How much more each tick for maze generation  (Higher number = slower)
show_grid = False


s = 64*12//(grid_size-1)
screen_s = grid_size*s, grid_size*s  # 65*12 or 129*6

# Colours
DarkGrey    = (15, 15, 15)
MedGrey     = (30, 30, 30)
Purple      = (167, 45, 255)
Orange      = (255, 167, 45)
Lime        = (45, 255, 167)
Red         = (200, 57, 43)
Blue        = (66, 135, 245)
DarkBlue    = (50, 54, 168)
Yellow      = (245, 200, 66)
Teal        = (25, 207, 176)
CoolGreen   = (116, 252, 159)


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
		self.text_surf = gui_font.render(text,True,'#FFFFFF')
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
		print("Click")

   
class Cell:
    color_dict = {'inactive': DarkGrey, 'evaluated': Yellow, 'active': Blue, 'barrier': Purple, 'start': DarkBlue, 'end': Lime, 'path': Red,
                  'runner': CoolGreen}
    def __init__(self, pos, size, grid, pos_in_grid, is_maze=False):
        self.pos = pos
        self.size = size
        self.type = 'inactive'
        
        self.f_cost = 0
        self.g_cost = 0
        self.h_cost = 0
        self.points_towards = None
        
        self.grid = grid
        self.x0, self.y0 = self.pos_in_grid = pos_in_grid
        self.grid_size = self.grid.size
        
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        
        if is_maze:
            self.type = 'barrier' if self.x0 % 2 == 0 or self.y0 % 2 == 0 else 'inactive'
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color_dict[self.type], self.rect)
        
    
    def get_neighbours(self,kernel_size=1, diags=False):
        if not diags:
            moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            neighbours = []
            x, y = self.pos_in_grid
            for i, j in moves:
                if 0 <= x+i < self.grid_size and 0 <= y+j < self.grid_size:
                    neighbours.append(self.grid.grid[x+i][y+j])
            return neighbours
        else:
            neighbours = []
            k = kernel_size
            for i in range(-k, k+1):
                if 0 <= self.x0 + i < self.grid_size:
                    for j in range(-k, k+1):
                        if 0 <= self.y0 + j < self.grid_size and not (i == 0 and j == 0):
                            neighbours.append(self.grid.grid[self.x0 + i][self.y0 + j])
            return neighbours

    def grid_neighbours(self):
        moves = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        neighbours = []
        x, y = self.pos_in_grid
        for i, j in moves:
            if 0 <= x+i < self.grid_size and 0 <= y+j < self.grid_size:
                neighbours.append(self.grid.grid[x+i][y+j])
        return neighbours
        

class Grid:
    def __init__(self, size, is_maze=False):
        self.size = size
        self.cell_size = [screen_s[0]/size, screen_s[1]/size]
        self.grid = []
        self.is_maze = is_maze
        
        self.grid_line_col = MedGrey
        
        self.has_start, self.has_end = False, False
        self.start, self.end, self.tracing = None, None, None
        self.is_generating = False
        
        self.is_solved = False
        self.traced = False
        self.has_path = True
        
        self.open_set = []
        self.closed_set = []
        
        for x in range(size):
            row = []
            for y in range(size):
                row.append(Cell((x*self.cell_size[0], y*self.cell_size[1]), self.cell_size, self, (x, y), is_maze=is_maze))
            self.grid.append(row)
        
        if is_maze:
            self.rand_cell = self.grid[rnd.randrange(1, size, 2)][rnd.randrange(1, size, 2)]
            # self.rand_cell.type = 'runner'
            self.stack = [self.rand_cell]
            self.current_cell = self.rand_cell
            self.rand_cell.type = 'runner'
            self.visited = []
            self.is_generating = False
            self.generated = False
    
    def __func__(self, x, y):
        return self.grid[x][y]
    
    def sq_at_pos(self, pos):
        return self.grid[int(pos[0]//self.cell_size[0])][int(pos[1]//self.cell_size[1])]
    
    def draw(self, screen):
        for row in self.grid:
            for cell in row:
                cell.draw(screen)
        
        if show_grid:
            for x in range(self.size):
                pygame.draw.line(screen, self.grid_line_col, (x*self.cell_size[0], 0), (x*self.cell_size[0], screen_s[1]))
            for y in range(self.size):
                pygame.draw.line(screen, self.grid_line_col, (0, y*self.cell_size[1]), (screen_s[0], y*self.cell_size[1]))
    
    def distance(self, c1, c2):  # Sort of like a cost function
        # Euclidean Distance (Diagonals are 1.4)
        if not self.is_maze: 
            return ((c1.pos_in_grid[0] - c2.pos_in_grid[0])**2 + (c1.pos_in_grid[1] - c2.pos_in_grid[1])**2)**(1/2)
    
        # Manhattan Distance (Diagonals are 2)
        else: 
            return (abs(c1.pos_in_grid[0] - c2.pos_in_grid[0]) + abs(c1.pos_in_grid[1] - c2.pos_in_grid[1]))
    
    def algorithm(self):
        if len(self.open_set) == 0:
            self.has_path = False
            return
        
        current = self.open_set[0] if len(self.open_set) == 1 else min(self.open_set, key=lambda x: x.f_cost)
            
        for neighbour in current.get_neighbours(diags=not self.is_maze):
            if neighbour.type == 'barrier': continue
            if neighbour in self.closed_set: continue
                
            dist = self.distance(current, neighbour)
            
            if neighbour.type == 'end':
                self.is_solved = True
                current.type = 'evaluated'
                neighbour.points_towards = current
                return

            elif neighbour.type == 'inactive':
                neighbour.g_cost = current.g_cost + dist
                neighbour.points_towards = current
                neighbour.h_cost = self.distance(self.end, neighbour)
                neighbour.f_cost = neighbour.g_cost + neighbour.h_cost
                neighbour.type = 'active' if not neighbour.type == 'evaluated' else 'evaluated'
                self.open_set.append(neighbour)

            elif neighbour.type == 'active':
                if current.g_cost + dist < neighbour.g_cost:
                    neighbour.g_cost = current.g_cost + dist
                    neighbour.points_towards = current
                    neighbour.h_cost = self.distance(self.end, neighbour)
                    neighbour.f_cost = neighbour.g_cost + neighbour.h_cost
        
        if not current.type == 'start':
            current.type = 'evaluated'
        self.open_set.remove(current)
        
    def trace_path(self):
        self.tracing = self.tracing.points_towards
        if self.tracing.type == 'start':
            self.traced = True
            return
        self.tracing.type = 'path'
    
    def generate_maze(self):
        # Using depth first search
        if len(self.stack) > 0:
            self.current_cell.type = 'inactive'
            self.current_cell = self.stack.pop()
            self.current_cell.type = 'runner'
            neighbours = [n for n in self.current_cell.grid_neighbours() if n not in self.visited]
            if len(neighbours) > 0:
                self.stack.append(self.current_cell)
                unv = rnd.choice(neighbours)  # TODO: Update this to runner
                (x1, y1), (x2, y2) = self.current_cell.pos_in_grid, unv.pos_in_grid
                self.grid[(x1+x2)//2][(y1+y2)//2].type = 'inactive'
                self.visited.append(unv)
                self.stack.append(unv)
                    
        else: 
            self.current_cell.type = 'inactive'
            self.is_generating = False
            self.generated = True
    
screen = pygame.display.set_mode((screen_s[0], screen_s[1]+100))
pygame.display.set_caption("Maze AI")
clock = pygame.time.Clock()

gui_font = pygame.font.SysFont('Comic Sans',20)
generate_maze_button = Button('Generate Maze', 230, 50, (20, screen.get_height()-75), 8)
find_path_button = Button('Find Path', 230, 50, (screen.get_width()-250, screen.get_height()-75), 8)


grid = Grid(grid_size)
counter = 0
start_alg = False
run = True
generate_grid = False

def start_pathfinding():
    global start_alg
    start_alg = True

def start_maze_generation():
    global generate_grid, grid
    if not generate_grid:
        grid = Grid(grid_size if grid_size % 2 == 1 else grid_size + 1, is_maze=True)
        grid.is_generating = not grid.is_generating
        generate_grid = True
        

find_path_button.press = start_pathfinding
generate_maze_button.press = start_maze_generation

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:  # Middle click: Inspect cell
                sq = grid.sq_at_pos(event.pos)
                print()
                print(f'Square at {sq.pos_in_grid}, Type: {sq.type}')
                print(f'G cost: {sq.g_cost:0.2f}')
                print(f'H cost: {sq.h_cost:0.2f}')
                print(f'F cost: {sq.f_cost:0.2f}')
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                start_path_finding()
                
            if event.key == pygame.K_ESCAPE:
                grid = Grid(grid_size)
                generate_grid = False
                start_alg = False
                
            if event.key == pygame.K_g and not generate_grid:
                start_maze_generation()
                
    if not start_alg:
        m_pos = pygame.mouse.get_pos()
        m_press = pygame.mouse.get_pressed()
        
        if m_press[0] and m_pos[1] <= screen_s[1]:  # Left click
            sq = grid.sq_at_pos(m_pos)
            if not grid.has_start:
                sq.type = 'start'
                grid.has_start = True
                grid.start = sq
                grid.open_set = [sq]
            elif not grid.has_end and sq.type != 'start':
                sq.type = 'end'
                grid.has_end = True
                grid.end = sq
                grid.tracing = sq
            else:
                if sq.type not in ['start', 'end']:
                    sq.type = 'barrier'
        elif m_press[2]:  # Right click
            sq = grid.sq_at_pos(m_pos)
            t = sq.type
            sq.type = 'inactive'
            if t == 'start': 
                grid.has_start = False
                grid.start = None
                grid.open_set = []
            elif t == 'end': 
                grid.has_end = False
                grid.end = None  
                grid.tracing = None      
    
    counter = (counter+1)%FPS
    
    if start_alg:
        if counter % ticks == 0 and grid.has_path:
            if not grid.is_solved: grid.algorithm()
            elif not grid.traced: grid.trace_path()
            
    if generate_grid:
        if grid.is_generating:
            if counter % (ticks*maze_senstivity) == 0:
                grid.generate_maze()
            
    
    grid.draw(screen)
    generate_maze_button.draw()
    find_path_button.draw()
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
