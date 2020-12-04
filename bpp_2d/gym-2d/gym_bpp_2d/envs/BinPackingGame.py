from __future__ import print_function
import sys
sys.path.append('.')
from .Game import Game
from .BinPackingLogic import Bin
import numpy as np
import random

class BinPackingGame(Game):

    def __init__(self, bin_width, bin_height, num_items, n):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.num_items = num_items
        self.n = n # number of bins (currently only one bin)

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Bin(self.bin_width, self.bin_height)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.bin_height, self.bin_width)

    def getActionSize(self):
        # return number of actions
        # return (self.bin_height*self.bin_width)*self.num_items
        return self.bin_height * self.bin_width * self.num_items

    def getInitItems(self, items_list):
        # items_list from item generator
        # 2D format
        items_list_board = []
        for i in range(self.num_items):
            w, h, _, _ = items_list[i]
            item_board = self.getInitBoard()
            item_board[0:h, 0:w] = 1
            items_list_board += [item_board]
        return items_list_board
    
    def getItemsUpdated(self, items_list_board, cur_item):
        # update items
        items_list_board[cur_item] -= items_list_board[cur_item] # set to 0     
        return items_list_board

    def getNextState(self, board, action, items_list_board):
        # get next board, to see if game ended - xw
        # also the next state to keep game going!
        # action must be a valid move
        items_list_board = np.copy(items_list_board)
        b = Bin(self.bin_width, self.bin_height)
        b.pieces = np.copy(board)

        # decode action to (item, placement)
        cur_item, placement = int(action/(self.bin_height*self.bin_width)), action%(self.bin_height*self.bin_width)        
        item = items_list_board[cur_item]
        assert sum(sum(item)) > 0 # must choose a valid item
        # if item is valid:
        w = sum(item[0,:])
        h = sum(item[:,0])
        move = (int(placement/self.bin_width), placement%self.bin_width)
        # execute action
        b.execute_move(move, w, h) # update bin
        items_list_board = self.getItemsUpdated(items_list_board, cur_item) # update items
        return (b.pieces, items_list_board)

    def getValidMoves(self, board):
        # return a binary vector
        # size is the same with getActionSize; the value is 1 for valid moves in the 'bin'
        valids = [0]*self.getActionSize()
        b = Bin(self.bin_width, self.bin_height)
        b.pieces = np.copy(board[0])
        legal_moves = []
        for item in range(self.num_items):
            if sum(sum(board[item+1])) == 0:
                continue
            legal_moves += b.get_moves_for_square(board[1:], item)
        assert len(legal_moves) > 0
        for item, x, y in legal_moves:
            valids[(item*(self.bin_height*self.bin_width)+x*self.bin_width+y)] = 1
        return np.array(valids)

    def has_valid_moves(self, board):
        # any valid move left? game ends or not
        b = Bin(self.bin_width, self.bin_height)
        b.pieces = np.copy(board[0])
        moves = []
        for item in range(self.num_items):
            if sum(sum(board[item+1])) == 0:
                # if all items placed, moves = []
                continue
            moves = b.get_moves_for_square(board[1:], item)
            if len(moves) > 0:
                break
        return len(moves) > 0

    def getGameEnded(self, total_board):
        # return 0 if game doesn't end; 1 if game ends
        assert(len(total_board) == self.num_items+self.n)
        if not self.has_valid_moves(total_board):
            # no legal moves left, game ends
            return 1
        else:
            return 0

    def getBinItem(self, board, items_list_board):
        # get the state: bin representation + items representation
        return np.array([board] + list(items_list_board))

    def getSymmetries(self, board, pi):
        # get symmetrical state representation
        # rotate 180 degree; flip in two ways
        assert(len(pi) == self.getActionSize())  # 1 for pass
        size_b = self.bin_width * self.bin_height
        pi_board = []
        for item in range(self.num_items):
            pi_board_ = np.reshape(pi[item*size_b:(item+1)*size_b], (self.bin_height, self.bin_width))
            pi_board.append(pi_board_)
        l = []
        for i in [2, 4]:
            newB = np.rot90(board, i)
            newPi = []
            pi_board_c = pi_board.copy()
            for item in range(self.num_items):
                pi_board_ = pi_board_c[item]
                newPi_ = np.rot90(pi_board_, i)
                newPi += list(newPi_.ravel())
            l += [(newB, list(np.copy(newPi)))]
        for i in [2, 4]:
            newB = np.rot90(board, i)
            newB = np.fliplr(newB)
            newPi = []
            pi_board_c = pi_board.copy()
            for item in range(self.num_items):
                pi_board_ = pi_board_c[item]
                newPi_ = np.rot90(pi_board_, i)
                newPi_ = np.fliplr(newPi_)
                newPi += list(newPi_.ravel())
            l += [(newB, list(np.copy(newPi)))]
        return l

    def get_minimal_bin(self, board):
        # evaluate packing result: minimal bin size
        # minimal_bin_size = max([h,w])^2
        for i in reversed(range(self.bin_height)):
            if sum(board[i,:]) > 0:
                break
        h = i + 1
        for j in reversed(range(self.bin_width)):
            if sum(board[:,j]) > 0:
                break
        w = j + 1
        a = max([h, w])
        return a
    
    def getReward(self, total_board, items_total_area):
        if sum(sum(total_board[0,:])) != items_total_area:
            # some items are discarded instead of being placed in the bin
            r = 0
        else:
            a = self.get_minimal_bin(total_board[0,:])
            r = items_total_area / (a*a)
        return r


class ItemsGenerator():

    def __init__(self, bin_width, bin_height, items):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.n = items

    def items_generator(self, seed):
        np.random.seed(seed)
        item_list = [[self.bin_width, self.bin_height, 0, 0]] # initial item equals to the bin

        while len(item_list) < self.n:
            axis = np.random.randint(2) # 0 for x , 1 for y axis
            idx_item = np.random.randint(len(item_list)) # choose an item to split
            [w, h, a, b] = item_list[idx_item]
            if axis == 0:
                if w == 1:
                    continue
                x_split = np.random.randint(a+1, a+w)
                new_w = x_split - a
                item_s1 = [new_w, h, a, b]
                item_list.append(item_s1)
                item_s2 = [w-new_w, h, x_split, b]
                item_list.append(item_s2)
                item_list.pop(idx_item)
            elif axis == 1:
                if h == 1:
                    continue
                y_split = np.random.randint(b+1, b+h)
                new_h = y_split - b
                item_s1 = [w, new_h, a, b]
                item_list.append(item_s1)
                item_s2 = [w, h-new_h, a, y_split]
                item_list.append(item_s2)
                item_list.pop(idx_item)
        return item_list

    # def items_generator_set_one_dim(self, seed, numbers_for_one_dim, mode='random'):
    #     # for 2D items: given the value of one dimension
    #     # generate items accordingly
    #     # mode: 
    #     #   'random' - the value of the other dimension is random (items won't perfectly fit a bin)
    #     #   'segmentation' - segment the bin to generate items that could fit (normal bin packing)
    #     np.random.seed()
    #     item_list = []
    #     if mode == 'random':
    #         while True:
    #             randomlist = list(range(1, 8))
    #             dim_values = random.choices(randomlist, k=len(numbers_for_one_dim))
    #             total_area = 0
    #             for i in range(len(numbers_for_one_dim)):
    #                 total_area += numbers_for_one_dim[i] * dim_values[i]
    #             if total_area <= 0.7 * 0.7 * self.bin_height * self.bin_width:
    #                 break
    #     for i in range(len(numbers_for_one_dim)):
    #         item_list.append([int(numbers_for_one_dim[i]), int(dim_values[i]), 0, 0])
    #     return item_list 