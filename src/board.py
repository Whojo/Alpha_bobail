#!/usr/bin/env python3

from copy import deepcopy
import numpy as np
from matplotlib import pyplot as plt
from typing import Optional
from random import choice, shuffle

from .player import Player, Token


Pos = (int, int)
Board = list[list[Token]]
BOARD_SIZE = 5


class NoBobailException(Exception):
    pass

class IllegalMove(Exception):
    pass

class BoardState:
    def _init_board(self) -> Board:
        return [
            [Token.GREEN, Token.GREEN, Token.GREEN , Token.GREEN, Token.GREEN],
            [Token.EMPTY, Token.EMPTY, Token.EMPTY , Token.EMPTY, Token.EMPTY],
            [Token.EMPTY, Token.EMPTY, Token.BOBAIL, Token.EMPTY, Token.EMPTY],
            [Token.EMPTY, Token.EMPTY, Token.EMPTY , Token.EMPTY, Token.EMPTY],
            [Token.RED  , Token.RED  , Token.RED   , Token.RED  , Token.RED  ],
        ]


    def __init__(self, board: Board = None, player_turn: Player = Player.RED):
        """
        Initializer of the class

        Arguments:
            - board (Board):
                The board state of the game
                If None instantiate to starting pos
            - player (Player):
                next player to play
        """
        if (board is None):
            board = self._init_board()

        self.board = board
        self.turn = player_turn

    def __eq__(self, other):
        if (not isinstance(other, BoardState)):
            return False

        return (self.board == other.board) and (self.turn == other.turn)

    def _get_bobail_pos(self) -> Pos:
        for i, row in enumerate(self.board):
            for j, token in enumerate(row):
                if (token is Token.BOBAIL):
                    return (i, j)

        raise NoBobailException()

    def _get_board_without_token(self, pos: Pos) -> 'BoardState':
        i, j = pos

        copy = deepcopy(self.board)
        copy[i][j] = Token.EMPTY

        return BoardState(copy, player_turn=self.turn)

    def _get_empty_pos_around(self, pos: Pos) -> list[Pos]:
        i, j = pos

        possible_future_pos = [
            (i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
            (i,     j - 1),             (i,     j + 1),
            (i + 1, j - 1), (i + 1, j), (i + 1, j + 1),
        ]
        return [
            (i_, j_) for (i_, j_) in possible_future_pos
            if (0 <= i_ < BOARD_SIZE) and (0 <= j_ < BOARD_SIZE)
                and (self.board[i_][j_] is Token.EMPTY)
        ]

    def _get_next_player(self):
        if (self.turn is Player.RED):
            return Player.GREEN
        else:
            return Player.RED

    def _switch_player(self):
        self.turn = self._get_next_player()

    def _duplicate(self) -> 'BoardState':
        board = deepcopy(self.board)
        return BoardState(board, player_turn=self.turn)

    def get_bobail_moves(self) -> list['BoardState']:
        """
        Generates all possible moves of the bobail
        """
        pos = self._get_bobail_pos()

        possible_future_pos = self._get_empty_pos_around(pos)
        board_with_no_bobail = self._get_board_without_token(pos)

        new_board_states = []
        for future_i, future_j in possible_future_pos:
            next_board_state = board_with_no_bobail._duplicate()
            next_board_state.board[future_i][future_j] = Token.BOBAIL
            new_board_states.append(next_board_state)

        return new_board_states

    def _get_random_bobail_move(self) -> 'BoardState':
        # TODO: opti by changing call to _get_empty_pos_around
        pos = self._get_bobail_pos()

        future_i, future_j = choice(self._get_empty_pos_around(pos))
        next_board_state = self._get_board_without_token(pos)
        next_board_state.board[future_i][future_j] = Token.BOBAIL

        return next_board_state


    def _get_token_turn_type(self) -> Token:
        if (self.turn is Player.RED):
            return Token.RED
        else:
            return Token.GREEN

    def _get_token_pos(self, token_type: Token) -> list[Pos]:
        token_pos = []

        for i, row in enumerate(self.board):
            for j, token in enumerate(row):
                if (token is token_type):
                    token_pos.append((i, j))

        return token_pos

    def _get_furthest_empty_pos(self, token_pos: Pos, delta_pos: Pos) -> Pos:
        i, j = token_pos
        alpha, beta = delta_pos

        furthest_pos = None
        for k in range(1, BOARD_SIZE):
            x, y = i + k * alpha, j + k * beta
            if (0 <= x < BOARD_SIZE and
                0 <= y < BOARD_SIZE and
                self.board[x][y] is Token.EMPTY):
                furthest_pos = (x, y)
            else:
                break

        return furthest_pos

    def _get_token_moves(self, token_pos: Pos, token_type: Token) -> list['BoardState']:
        delta_pos_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1),          (0,  1),
            (1,  -1), (1,  0), (1,  1),
        ]

        board_without_current_token = self._get_board_without_token(token_pos)
        board_without_current_token._switch_player()

        new_board_states = []
        for delta_pos in  delta_pos_list:
            furthest_pos = self._get_furthest_empty_pos(token_pos, delta_pos)
            if (not furthest_pos):
                continue

            i, j = furthest_pos
            next_board_state = board_without_current_token._duplicate()
            next_board_state.board[i][j] = token_type
            new_board_states.append(next_board_state)

        return new_board_states

    def get_tokens_moves(self) -> list['BoardState']:
        """
        Returns all next board state
        """
        token_turn_type = self._get_token_turn_type()
        token_pos = self._get_token_pos(token_turn_type)

        return [
            board_state
            for pos in token_pos
            for board_state in self._get_token_moves(pos, token_turn_type)
        ]

    def _get_random_token_move(self) -> 'BoardState':
        token_type = self._get_token_turn_type()
        token_pos = choice(self._get_token_pos(token_type))

        delta_pos_list = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1),          (0,  1),
            (1,  -1), (1,  0), (1,  1),
        ]
        shuffle(delta_pos_list)

        next_board_state = self._get_board_without_token(token_pos)
        next_board_state._switch_player()

        for delta_pos in delta_pos_list:
            furthest_pos = self._get_furthest_empty_pos(token_pos, delta_pos)
            if (furthest_pos is not None):
                i, j = furthest_pos
                next_board_state.board[i][j] = token_type

                return next_board_state

        raise RuntimeException("No possible moves ?")

    def _is_bobail_on_line(self, pos: Pos) -> Optional[Player]:
        i, _ = pos

        if (i == 0):
            return Player.GREEN
        if (i == BOARD_SIZE - 1):
            return Player.RED

        return None

    def _is_bobail_stuck(self, pos: Pos) -> bool:
        return len(self._get_empty_pos_around(pos)) == 0

    def do_move(self, start_pos: Pos, dest_pos: Pos) -> None:
        """
        Apply a move (encoded with 2 positions) to the current board
        Also checks the validity of the move
        """
        si, sj = start_pos
        di, dj = dest_pos

        start_token = self.board[si][sj]
        if (start_token in (Token.RED, Token.GREEN)):
            valid_moves = self.get_tokens_moves()
            self._switch_player()
        elif (start_token is Token.BOBAIL):
            valid_moves = self.get_bobail_moves()
        else:
            raise IllegalMove("Trying to move an empty token")

        self.board[di][dj] = start_token
        self.board[si][sj] = Token.EMPTY

        if (self not in valid_moves):
            raise IllegalMove()


    def get_state(self):
        """
        Returns which player won the game or None
        """
        pos = self._get_bobail_pos()
        player = self._is_bobail_on_line(pos)
        if (player is not None):
            return player

        if (self._is_bobail_stuck(pos)):
            return self._get_next_player()

        return None

    def finish_random(self): # TODO: refacto to select randomly the pieces and the direction instead of a move (x15)
        board = self
        while (board.get_state() is None):
            # board = self._get_random_bobail_move()
            board = choice(board.get_bobail_moves())
            # board = self._get_random_token_move()
            board = choice(board.get_tokens_moves())

        return board

    def _get_score(self, batch_size) -> int:
        score = 0

        for i in range(batch_size):
            new_board = self._duplicate()
            new_board = new_board.finish_random()
            if (new_board.get_state() == Player.RED): # TODO: Remove this shit
                score += 1

        return score

    def get_best_move(self, batch_size=10) -> 'BoardState':
        """
        """
        best_move = None
        best_score = 0

        possible_moves = [
            token_board
            for bobail_board in self.get_bobail_moves()
            for token_board in bobail_board.get_tokens_moves()
        ]
        for move in possible_moves:
            score = move._get_score(batch_size=batch_size)

            if (score > best_score):
                best_move = move
                best_score = score

        return best_move

    def render_board_state(self) -> np.array:
        """
        Returns a PIL image of the current board state
        """

        color_switcher = {
            Token.BOBAIL: (232, 227, 75),
            Token.RED: (196, 43, 43),
            Token.GREEN: (40, 181, 78),
            Token.EMPTY: (205, 133, 63),
        }

        image = np.asarray([
            [color_switcher[token] for token in row]
            for row in self.board
        ])

        return image
