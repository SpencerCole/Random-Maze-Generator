import argparse
import os
import random
import sys
import time
import timeit


class Maze(object):

	def __init__(self, width=None, height=None, speed=None, show_steps=None, no_print=None, raw=None, seed=None):
		# TODO: Generate and Capture random seed.
		self.width = width
		self.height = height
		self.speed = speed
		self.show_steps = show_steps
		self.no_print = no_print
		self.raw = raw
		self.mapping = {'[0, 0]': '  ',
						'[1, 0]': '| ',
						'[0, 1]': '``',
						'[1, 1]': '|`',
						'#': ' #',
						'@': ' @'}
		self.previous_cells = []
		self.visited_cells = []
		self.current_cell = [0,0]
		self.visited_cells.append(list(self.current_cell))
		self.previous_cells.append(list(self.current_cell))
		self.has_exit = False
		self.seed = seed or int(time.time())
		self.progress_pos = 0
		random.seed(self.seed)
		self._generate()

	def __repr__(self):
		self._mazeString()
		return self.maze_raw_buf

	def __str__(self):
		self._mazeString()
		return self.maze_display_buf


	def _chooseNeighbor(self):
		unvisited_neighbors = []

		up = None
		dn = None
		lt = None
		rt = None

		if self.current_cell[0] - 1 >= 0:
			up = [self.current_cell[0] - 1, self.current_cell[1], 'up']
			if up and up[:2] not in self.visited_cells:	unvisited_neighbors.append(up)
		if self.current_cell[0] + 1 < self.height:
			dn = [self.current_cell[0] + 1, self.current_cell[1], 'dn']
			if dn and dn[:2] not in self.visited_cells:	unvisited_neighbors.append(dn)
		if self.current_cell[1] - 1 >= 0:
			lt = [self.current_cell[0], self.current_cell[1] - 1, 'lt']
			if lt and lt[:2] not in self.visited_cells:	unvisited_neighbors.append(lt)
		if self.current_cell[1] + 1 < self.width:
			rt = [self.current_cell[0], self.current_cell[1] + 1, 'rt']
			if rt and rt[:2] not in self.visited_cells: unvisited_neighbors.append(rt)

		return random.choice(unvisited_neighbors) if unvisited_neighbors else None


	def _makeExit(self):
		# TODO Add weights depending on dimensions of the maze.
		# 1x5 maze should have its exit at the bottom.
		# 5x1 maze should have it exit as the end.

		edge = None
		# This usually makes the exit right next to the entrance.
		#if self.current_cell[0] - 1 < 0:
		#	edge = 'up'
		#	cell = list(self.current_cell)
		if self.current_cell[1] - 1 < 0:
			edge = 'lt'
			cell = list(self.current_cell)
		elif self.current_cell[1] + 1 >= self.width:
			edge = 'rt'
			cell = list(self.current_cell)
			cell[1] += 1
		elif self.current_cell[0] + 1 >= self.height:
			edge = 'dn'
			cell = list(self.current_cell)
			cell[0] += 1

		if edge:
			cell.append(edge)
			self._removeWall(cell)
			self.has_exit = True


	def _removeWall(self, cell):
		if cell[2] == 'up': # 10
			self.maze[self.current_cell[0]][self.current_cell[1]][1] = 0

		if cell[2] == 'lt': # 01
			self.maze[self.current_cell[0]][self.current_cell[1]][0] = 0

		if cell[2] == 'dn': # 10
			self.maze[cell[0]][cell[1]][1] = 0

		if cell[2] == 'rt': # 01
			self.maze[cell[0]][cell[1]][0] = 0


	def _generate(self):
		# Build basic maze form
		self.maze = []
		for row in range(self.height):
			maze_row = []
			for col in range(self.width):
				maze_row.append([1, 1])
			self.maze.append(list(maze_row))

		# Make the entrance
		self.maze[0][0] = [1, 0]

		# Add ending columns edges
		for row in self.maze:
			row.append([1, 0])

		# Add bottom row bottoms
		bottom_row = []
		for i in range(self.width + 1):
			bottom_row.append([0, 1])
		self.maze.append(bottom_row)

		# Fix last box on the furthest edges (height, width)
		self.maze[self.height][self.width] = [0, 0]

		while self.previous_cells:
			neighbor = self._chooseNeighbor()
			# choose random neighbor thats not been visited
			if neighbor:
				# push current cell to previous stack
				if self.current_cell not in self.previous_cells:
					self.previous_cells.append(list(self.current_cell))
				# remove wall between
				self._removeWall(neighbor)
				self.current_cell = neighbor[:2]
				# make new cell the current cell and mark it as visited
				if self.current_cell not in self.visited_cells:
					self.visited_cells.append(list(self.current_cell))
			#if no neighbor and the stack is not empty
			else:
				if not self.has_exit: self._makeExit()
				self.current_cell = self.previous_cells.pop()

			if self.show_steps:
				self._print()
				time.sleep(self.speed)

			# Disply a progress bar
			sys.stdout.write('\b' * 10 + self._progress())
			sys.stdout.flush()

		if not self.no_print:
			self._print()
			self._write()


	def _progress(self):
		self.progress_pos += 1
		status_bar = ['|', '/', '-', '\\']
		if self.progress_pos >= len(status_bar):
			self.progress_pos = 0
		percent = '{0:.0%}'.format(float(len(self.visited_cells)) / float(self.width * self.height))
		return status_bar[self.progress_pos] + percent


	def _write(self):
		filename = '{} x {} - {}.txt'.format(self.width, self.height, time.ctime())
		file = open(filename, 'w')
		file.write(self.maze_display_buf)
		file.write('Seed: '+ str(self.seed))
		file.close()

	def _translate(self, num):
		return self.mapping[num]

	def _mazeString(self):
		self.maze_display_buf = ''
		self.maze_raw_buf = ''
		for i, row in enumerate(self.maze):
			for x, col in enumerate(row):
				# Show current position
				if self.current_cell == [i, x] and self.previous_cells:
					self.maze_display_buf += self._translate('#')
				# Show history of positions
				elif [i, x] in self.previous_cells:
					self.maze_display_buf += self._translate('@')
				# Show borders
				elif [i, x] not in self.visited_cells and i < len(self.maze) - 1 and x < len(self.maze[0]) - 1:
					self.maze_display_buf += self._translate('[0, 0]')
				# Show the rest
				else:
					self.maze_display_buf += self._translate(str(col))
				self.maze_raw_buf += str(col)
			self.maze_display_buf += '\n'



	def _print(self):
		self._mazeString()
		os.system('clear')
		if not self.raw:
			sys.stdout.write(self.maze_display_buf)
			sys.stdout.flush()
		else:
			sys.stdout.write(self.maze_raw_buf)
			sys.stdout.flush()


def main():
	parser = argparse.ArgumentParser(description='Random Maze Generator')
	parser.add_argument('--width', required=True, type=int, help='(X > 1) an integer for the width of the maze.')
	parser.add_argument('--height', required=True, type=int, help='(X > 1) an integer for the height of the maze.')
	parser.add_argument('--seed', type=int, help='an integer seed for the random module to generate the maze.')
	parser.add_argument('--speed', default=0.07, type=float, help='a float for the speed of the show_steps generation.')
	parser.add_argument('--show_steps', default=False, action='store_true', help='a flag to show the maze construction.')
	parser.add_argument('--no_print', default=False, action='store_true', help='a flag to show the maze after construction.')
	parser.add_argument('--raw', default=False, action='store_true', help='a flag to show the raw maze numbers.')
	parser.add_argument('--test_runs', type=int, help='an integer for the number of iterations to run the time test against.')
	args = parser.parse_args()

	if args.test_runs:
		start_time = time.clock()
		for x in range(args.test_runs):
			Maze(width=args.width, height=args.height, show_steps=False, no_print=True, raw=False)
		process_time = time.clock() - start_time
		print '\nIt took {}\'s to process {} mazes of that size. {}\'s per maze.'.format(process_time, args.test_runs, (process_time/args.test_runs))

	else:
		if args.show_steps:
			args.raw = False

		m = Maze(width=args.width, height=args.height, speed=args.speed, show_steps=args.show_steps,
				 no_print=args.no_print, raw=args.raw, seed=args.seed)

		# Prints the maze
		#print m

		# Prints the mazes raw tables
		#print repr(m)


if __name__ == '__main__':
	main()