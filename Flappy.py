import os, pickle, time
import neat, random
import pygame

pygame.font.init()

WIN_WIDTH = 576  # actually, the bg.png is only 576px wide
WIN_HEIGHT = 960
FPS = 30  # There are 30.0 frames in every seconds.
DPM = 100  # There are 100.0 dots (pixels) in every meters
# flappy bird is 34px by 24px, flying with its vertical speed velocity as 1.2 m/s

BIRD_IMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")),
			 pygame.image.load(os.path.join("imgs", "bird2.png")),
			 pygame.image.load(os.path.join("imgs", "bird3.png"))]  # <class 'pygame.Surface'>
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 32)

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 5
	ANIMATION_TIME = 5

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y  # explain at (1, 10:00)
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		self.vel -= 4.0  # ~ 1.2 m/s
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		self.vel += 9.80665 * DPM/FPS**2  # 9.8 m/s**2 = 9.8 (DPM*pixel)/(FPS*frame)**2 = (9.8 * (DPM/FPS**2)) pixel/frame**2
		#  d = self.vel*self.tick_count + 1.5*self.tick_count**2  # it seems that Tim confused the displacement with velocity!

		if self.vel >= 16:
			v = 16  # = 4.8m/s * 1/30s * 100px/m

		if self.vel < -16:
			v = -16

		self.y += round(self.vel)

		if self.vel < 4:  # ~ 1.2 m/s
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4+1:
			self.img = self.IMGS[0]
			self.img_count = 0
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2

		rotated_image = pygame.transform.rotate(self.img, self.tilt)  # rotated on the top-left
		new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)  # the following line, Tim copied this from the Stack Overflow.
		win.blit(rotated_image, new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe:
	GAP = 100  # = 1m * 100px/m
	VEL = 4  # = 1.2m/s * 1/30s * 100px/m

	def __init__(self, x, easy=0.0):  # easy: 1 (easy) to 0 (difficult)
		self.x = x
		self.height = 0
		self.GAP = round(128 + easy * 64)

		self.top = 100
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG  # explain at (2, 2:10)

		self.passed = False
		self.set_height(easy)

	def set_height(self, easy=0.0):
		self.height = random.randrange(64, 704-self.GAP)
		self.top = self.height - self.PIPE_TOP.get_height()  # refer to the documentary
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top))
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

	def collide(self, bird):
		bird_mask = bird.get_mask()
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y))
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset)
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point:
			return True

		return False




class Base:
	VEL = 4  # = 1.2m/s * 1/30s * 100px/m
	WIDTH = BASE_IMG.get_width()  # data type of the BASE_IMG?
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH  # explain at (3, 18:00)

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
	win.blit(BG_IMG, (0, 0))

	for pipe in pipes:
		pipe.draw(win)

	text = STAT_FONT.render("Score: "+ str(score), 1, (255,255,255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 16))
	text = STAT_FONT.render("gen: " + str(gen), 1, (255, 255, 255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 48))
	text = STAT_FONT.render("alive: " + str(len(birds)), 1, (255, 255, 255))
	win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 80))

	base.draw(win)

	for bird in birds:
		bird.draw(win)

	pygame.display.update()


class CONFIG:
	def __init__(self):
		self.GEN = 0
		self.SCORE_WIN = 30

CFG = CONFIG()


def iter(genomes, config):
	nets = []
	ge = []
	birds = []
	
	'''
	print(type(config))
	for attribute_name in config.__dict__:
		print(type(getattr(config, attribute_name)), attribute_name, "=", getattr(config, attribute_name))
	print(config.fitness_threshold)
	'''

	for _, g in genomes:  # fix-1
		net = neat.nn.FeedForwardNetwork.create(g, config)  # explain
		nets.append(net)
		birds.append(Bird(150, 384))
		g.fitness = 0  # fitness function: physical distance it go in the game
		ge.append(g)
	# birds = [] ########################## This single line cost your about 30 minutes
	base = Base(768)
	pipes = [Pipe(3000, 1)]  # explain (4, 2:10)
	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
	clock = pygame.time.Clock()

	score = 0

	run = True
	while run:
		clock.tick(FPS)
		for event in pygame.event.get():  # pygame.event.get() returns an array (usually empty unless you click on mouse or press keys), event iterates through that array
			if event.type == pygame.QUIT:  # if any element of that array has a element contain an element which .type attribute equals pygame.QUIT
				run = False, pygame.quit(), quit()

		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
				pipe_ind = 1  # explain
		else:
			CFG.GEN += 1
			run = False
			break

		for x, bird in enumerate(birds):
			bird.move()
			ge[x].fitness += 1.2/FPS
		
		for g in ge:
			if g.fitness >= config.fitness_threshold:  # threshold in config file
				run = False
		if run == False:
			break
		
		for x, bird in enumerate(birds):
			output = nets[x].activate((max(pipes[0].x - 150, -50), bird.y, bird.y - (pipes[pipe_ind].height+pipes[pipe_ind].bottom)/2, bird.vel))
			if output[0] > 0.5:  # fix-2
				bird.jump()

		add_pipe = False
		rem = []
		for pipe in pipes:
			for x, bird in enumerate(birds):  # remove collides and
				if pipe.collide(bird):
					# ge[x].fitness -= 1.2 * 10 / FPS  # explain-4
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)

			if (len(birds) > 0) == False:
				CFG.GEN += 1
				run = False
				break

			if not pipe.passed and pipe.x < birds[0].x:
				pipe.passed = True
				add_pipe = True

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:
				rem.append(pipe)

			pipe.move()

		if add_pipe:
			score += 1  # for every survived bird
			for g in ge:
				g.fitness += 2  # pass the pipe has save reward as fly 2 meters
			for g in ge:
				if g.fitness >= config.fitness_threshold:  # threshold in config file
					run = False
					break
			if run == False:
				break
			pipes.append(Pipe(1000, max(1-score/10, 0)))

		for r in rem:
			pipes.remove(r)

		for x, bird in enumerate(birds):  # explain: enumerate
			if bird.y + bird.img.get_height() >= 768 or bird.y < 0:
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)

		base.move()
		draw_window(win, birds, pipes, base, score, CFG.GEN)



def main():
	config_file_name = "config-feedforward.txt"
	MAX_ITER = 30
	model_file_name = "finalized_model.pickle"
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_file_name)

	p = neat.Population(config)  # explain 2
	
	for attr_name in p.__dict__:
		print(type(getattr(p, attr_name)), attr_name, "=", getattr(p, attr_name))
	
	p.add_reporter(neat.StdOutReporter(True))  # explain 3
	p.add_reporter(neat.StatisticsReporter())  # explain 5

	winner = p.run(iter, MAX_ITER)  # explain 6

	# pickle.dump(winner, open(model_file_name, "wb"))
	# loaded_model = pickle.load(open(model_file_name, 'rb'))


if __name__ == "__main__":
	main()












###########################################################
# 1: to set up
# 2: to get birds
# 3: to the pipes and base
# 4: get together and make them move
# 5:
# What the input to be in the neural network?
'''
Inputs:
	Bird.y, top_pipe, bottom_pipe
Output:
	Jump or not (Decision)
Activation Function:
	tanh, sigmoid is also OK, but Tim prefer tanh 
Population Size:
	start with 100, random networks ctrl the birds
	test all of them, and mutate (something like genetic alg)   
Fitness Function (some software redistributions called 'Loss Function'):
	by far, the most important part in the alg
	a way to eval how good the birds are
	mean-score? margins?
	use: distance of every individuals
Max Generations:
	set 30
'''
# 6: the module implemented, ge, net and more
# 7:


