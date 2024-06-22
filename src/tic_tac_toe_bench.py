import logging
from inspect_ai import Task, task
from inspect_ai.scorer import Metric, mean, metric, scorer
from inspect_ai.dataset import Dataset, Sample
import inspect_ai.dataset
from inspect_ai.solver import solver, Solver, generate, Generate, TaskState
from inspect_ai.dataset import MemoryDataset
import tic_tac_toe
from inspect_ai.model import ChatMessageUser



@solver
def play_tic_tac_toe(opponent_cls):
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        game = tic_tac_toe.TicTacToe()
        # todo: randomize player order
        opponent = opponent_cls()
        message = game.board_to_string() + "\n\n" + game.current_player + " to move" + "Please enter a number between 0 and 8."
        state.messages.append(ChatMessageUser(content=message))
        while not game.winner:
            if game.current_player == 'X':
                move = opponent.get_move(game)
            else:
                # TODO
                move = await generate()
            game.make_move(move)
            message = game.current_player + f"plays at {move}" + "\n\n" + game.board_to_string() + "\n\n" + game.current_player + " to move" + "Please enter a number between 0 and 8."



@task
def tic_tac_toe_eval(bot_cls, num_games: int = 1000):
    dataset = MemoryDataset([Sample(input=str(i+1)) for i in range(num_games)])
    plan = [
        play_tic_tac_toe(opponent=bot_cls)
    ]
    scorer = parse_score()

    return Task(dataset, plan, scorer)