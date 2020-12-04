import gym
from gym import error, spaces, utils
from gym.utils import seeding

from .BinPackingGame import BinPackingGame as Game
from .BinPackingGame import ItemsGenerator as Generator

class BppEnv(gym.Env):
    def __init__(self, bin_height=10, bin_width=10, num_items=10, bin_height_virtual=15, bin_width_virtual=15, seed=[]):
        # init environment with default parameters
        # bin_height, bin_width: the 'optimal' bin size; generate items by slicing the bin (bin_height, bin_width)
        self.bin_height, self.bin_width = bin_height, bin_width
        # number of items
        self.num_items = num_items
        # pack items into a 'virtual' bin; the goal is to find the minimal packing;
        # the size of this 'virtual' bin decides the size of the state representation
        self.bin_height_virtual, self.bin_width_virtual = bin_height_virtual, bin_width_virtual
        # set seed
        if len(seed) == 0:
            self.seed = 0 # default seed
        else:
            self.seed = seed

        # initialize items by slicing a bin with size bin_height * bin_width
        self.gen = Generator(bin_width, bin_height, num_items)
        # generate items using self.seed
        items_list = self.gen.items_generator(self.seed)
        self.items_list = items_list.copy()
        # initialize bin packing problem as a game
        self.game = Game(bin_width_virtual, bin_height_virtual, num_items, n=1)

        # initial empty bin and items
        # board = the virtual bin
        board = self.game.getInitBoard()
        self.board = board.copy()
        items_list_board = self.game.getInitItems(self.items_list)
        self.items_list_board = items_list_board.copy()
        bin_items_state = self.game.getBinItem(board, items_list_board)
        self.state = bin_items_state.copy()
        # the total area of items
        self.items_total_area = sum(sum(sum(items_list_board)))

        # step
        self.step = 0
        self.max_step = 100

        # action space
        # action: choose an item from N items + choose a position for the item in the virtual bin
        # N * virtual_height * virtual_width
        self.action_space = spaces.Discrete(self.game.getActionSize())

    def init_par(self, bin_height, bin_width, num_items, bin_height_virtual, bin_width_virtual, seed=[]):
        # to set parameters, use this the function
        self.bin_height, self.bin_width = bin_height, bin_width
        self.num_items = num_items
        self.bin_height_virtual, self.bin_width_virtual = bin_height_virtual, bin_width_virtual
        if len(seed) == 0:
            self.seed = 0 # default seed
        else:
            self.seed = seed

        # initialize items by slicing a bin with size bin_height * bin_width
        self.gen = Generator(bin_width, bin_height, num_items)

        items_list = self.gen.items_generator(self.seed)
        self.items_list = items_list.copy()
        # initialize bin packing problem
        self.game = Game(bin_width_virtual, bin_height_virtual, num_items, n=1)

        # initial empty bin and items
        board = self.game.getInitBoard()
        self.board = board.copy()
        items_list_board = self.game.getInitItems(self.items_list)
        self.items_list_board = items_list_board.copy()
        bin_items_state = self.game.getBinItem(board, items_list_board)
        self.state = bin_items_state.copy()
        self.items_total_area = sum(sum(sum(items_list_board)))

        # action space
        self.action_space = spaces.Discrete(self.game.getActionSize())


    def step(self, action):
        self.step += 1
        exceed_max_step = self.step > self.max_step

        valid_actions = self.game.getValidMoves(self.state)
        if valid_actions[action] != 1:
            return self.state.copy(), 0, 0 or exceed_max_step, []

        board, items_list_board = self.game.getNextState(self.board, action, self.items_list_board)
        self.board = board.copy()
        self.items_list_board = items_list_board.copy()
        next_bin_items_state = self.game.getBinItem(board, items_list_board)
        self.state = next_bin_items_state.copy()


        done = self.game.getGameEnded(next_bin_items_state)
        if not done:
            r = 0
        else:
            r = self.game.getReward(next_bin_items_state, self.items_total_area)

        return self.state.copy(), r, done or exceed_max_step, []

    def reset(self):
        items_list = self.gen.items_generator(self.seed)
        self.items_list = items_list.copy()
        # initialize bin packing problem
        self.game = Game(self.bin_width_virtual, self.bin_height_virtual, self.num_items, n=1)

        # initial empty bin and items
        board = self.game.getInitBoard()
        self.board = board.copy()
        items_list_board = self.game.getInitItems(self.items_list)
        self.items_list_board = items_list_board.copy()
        bin_items_state = self.game.getBinItem(board, items_list_board)
        self.state = bin_items_state.copy()
        self.items_total_area = sum(sum(sum(items_list_board)))
        self.step = 0
        return self.state

    def render(self):
        pass
