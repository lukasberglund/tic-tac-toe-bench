from typing import List, Dict, Tuple, Optional, Union
import math
import random
from abc import ABC, abstractmethod

class TicTacToe:
    def __init__(self) -> None:
        self.board: List[str] = [' ' for _ in range(9)]
        self.current_player: str = 'X'
        self.winner: Optional[str] = None

    def make_move(self, position: int) -> bool:
        if self.winner or position < 0 or position > 8 or self.board[position] != ' ':
            return False

        self.board[position] = self.current_player
        if self.check_winner():
            self.winner = self.current_player
        elif ' ' not in self.board:
            self.winner = 'Tie'
        else:
            self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def check_winner(self) -> bool:
        win_conditions: List[List[int]] = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
            [0, 4, 8], [2, 4, 6]  # diagonals
        ]
        return any(self.board[a] == self.board[b] == self.board[c] != ' '
                   for a, b, c in win_conditions)

    def get_state(self) -> Dict[str, Union[List[str], str, None]]:
        return {
            'board': self.board,
            'current_player': self.current_player,
            'winner': self.winner
        }

    def print_board(self) -> None:
        for i in range(0, 9, 3):
            print(' | '.join(self.board[i:i+3]))
            if i < 6:
                print('---------')

    def board_to_string(self) -> str:
        rows: List[str] = [
            ' | '.join(self.board[i:i+3])
            for i in range(0, 9, 3)
        ]
        return '\n---------\n'.join(rows)

class Bot(ABC):
    def __init__(self, player: str) -> None:
        self.player: str = player

    @abstractmethod
    def get_move(self, game: TicTacToe) -> int:
        pass

class TicTacToeBot(Bot):
    def __init__(self, player: str, top_n: int = 3) -> None:
        super().__init__(player)
        self.top_n: int = top_n

    def get_move(self, game: TicTacToe) -> int:
        moves: List[Tuple[int, int]] = self.rank_moves(game)
        best_moves: List[Tuple[int, int]] = moves[:min(self.top_n, len(moves))]
        return random.choice(best_moves)[1]

    def rank_moves(self, game: TicTacToe) -> List[Tuple[int, int]]:
        moves: List[Tuple[int, int]] = []
        for move in range(9):
            if game.board[move] == ' ':
                game.board[move] = self.player
                game.current_player = 'O' if self.player == 'X' else 'X'
                
                if game.check_winner():
                    game.winner = self.player
                elif ' ' not in game.board:
                    game.winner = 'Tie'

                score, _ = self.minimax(game, game.current_player, float('-inf'), float('inf'))
                moves.append((score, move))

                game.board[move] = ' '
                game.current_player = self.player
                game.winner = None

        return sorted(moves, reverse=True)

    def minimax(self, game: TicTacToe, player: str, alpha: float, beta: float) -> Tuple[int, Optional[int]]:
        if game.winner:
            if game.winner == self.player:
                return 1, None
            elif game.winner == 'Tie':
                return 0, None
            else:
                return -1, None

        best_score: int = float('-inf') if player == self.player else float('inf')
        best_move: Optional[int] = None

        for move in range(9):
            if game.board[move] == ' ':
                game.board[move] = player
                game.current_player = 'O' if player == 'X' else 'X'
                
                if game.check_winner():
                    game.winner = player
                elif ' ' not in game.board:
                    game.winner = 'Tie'

                score, _ = self.minimax(game, game.current_player, alpha, beta)

                game.board[move] = ' '
                game.current_player = player
                game.winner = None

                if player == self.player:
                    if score > best_score:
                        best_score = score
                        best_move = move
                    alpha = max(alpha, best_score)
                else:
                    if score < best_score:
                        best_score = score
                        best_move = move
                    beta = min(beta, best_score)

                if beta <= alpha:
                    break

        return best_score, best_move

class RandomBot(Bot):
    def get_move(self, game: TicTacToe) -> int:
        available_moves: List[int] = [i for i, spot in enumerate(game.board) if spot == ' ']
        return random.choice(available_moves)

if __name__ == '__main__':
    def play_game(player_x: Union[str, Bot], player_o: Union[str, Bot]) -> None:
        game: TicTacToe = TicTacToe()
        players: Dict[str, Union[str, Bot]] = {'X': player_x, 'O': player_o}

        while not game.winner:
            print(game.board_to_string())  # Use the new method here
            current_player: Union[str, Bot] = players[game.current_player]
            
            if isinstance(current_player, Bot):
                print(f"AI ({game.current_player}) is thinking...")
                move: int = current_player.get_move(game)
                print(f"AI chose position {move}")
            else:
                print(f"Player {game.current_player}'s turn")
                while True:
                    try:
                        move: int = int(input("Enter your move (0-8): "))
                        if game.make_move(move):
                            break
                        else:
                            print("Invalid move, try again.")
                    except ValueError:
                        print("Please enter a number between 0 and 8.")
            
            game.make_move(move)

        print(game.board_to_string())  # Use the new method here
        if game.winner == 'Tie':
            print("It's a tie!")
        else:
            print(f"Player {game.winner} wins!")

        print("Final game state:", game.get_state())

    # Example usage
    smart_bot: TicTacToeBot = TicTacToeBot('O', top_n=2)
    random_bot: RandomBot = RandomBot('X')

    # Uncomment one of the following lines to play different game modes:
    play_game(RandomBot('X'), RandomBot('O'))  # Random vs Random
    # play_game("Human", RandomBot('O'))  # Human vs Random
    # play_game("Human", smart_bot)  # Human vs Smart Bot
    # play_game(RandomBot('X'), smart_bot)  # Random vs Smart Bot