'''
Author: Eric P. Nichols
Date: Feb 8, 2008.
Board class.
Board data:
  1=white, -1=black, 0=empty
  first dim is column , 2nd is row:
     pieces[1][7] is the square in column 2,
     at the opposite end of the board in row 8.
Squares are stored and manipulated as (x,y) tuples.
x is the column, y is the row.
'''

"""
Inherited from OthelloLogic.py, for bin configuration in bin packing problem.
"""
import numpy as np

class Bin():

    def __init__(self, bin_width, bin_height):
        "Set up initial bin configuration."
        self.bin_width = bin_width
        self.bin_height = bin_height
        # Create the empty bin array, height * width
        self.pieces = [None]*self.bin_height
        for i in range(self.bin_height):
            self.pieces[i] = [0]*self.bin_width

    # add [][] indexer syntax to the Bin
    def __getitem__(self, index): 
        return self.pieces[index]

    def get_adjacency(self, i, j, h, w):
        # important: adjacency rule
        # for a placement to be valid, the item must be adjacent to either the bin boarder or other items
        # in two adjacent dimensions (here it is up and left)
        adjacent_direction = 0
        # get adjacency information for current item (h, w) if placed in (i, j)
        ## up
        if i == 0:
            adjacent_direction += 1
        else:
            if sum(self[i-1, j:j+w]) != 0:
                adjacent_direction += 1
        ## down
        # if i+h == self.bin_height:
        #     adjacent_direction += 1
        # else:
        #     if sum(self[i+h, j:j+w]) != 0:
        #         adjacent_direction += 1
        ## left
        if j == 0:
            adjacent_direction += 1
        else:
            if sum(self[i:i+h, j-1]) != 0:
                adjacent_direction += 1
        ## right
        # if j+w == self.bin_width:
        #     adjacent_direction += 1
        # else:
        #     if sum(self[i:i+h, j+w]) != 0:
        #         adjacent_direction += 1
        # at least having adjacency in two directions
        return adjacent_direction == 2

    def get_moves_for_square(self, items_list_board, item_idx):
        # get moves for each available item
        item = items_list_board[item_idx] # 2d format
        assert sum(sum(item)) > 0
        w = sum(item[0,:])
        h = sum(item[:,0]) 
        moves = []
        # current item to be placed
        for i in range(self.bin_height-h+1):
            for j in range(self.bin_width-w+1):
                if sum(sum(self[i:i+h, j:j+w])) == 0:
                    adjacent = self.get_adjacency(i, j, h, w)
                    if adjacent:
                        moves.append((item_idx, i, j))
        return moves

    def execute_move(self, move, w, h):
        """Only update the bin.
        """
        # return new bin and new items_all
        # move: (i, j)
        # items_list = items_list.copy()
        pieces = self.pieces.copy()
        i, j = move
        assert(sum(sum(pieces[i:i+h, j:j+w])) == 0)
        pieces[i:i+h, j:j+w] = 1
        self.pieces = pieces.copy()