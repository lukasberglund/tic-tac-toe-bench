import logging
from inspect_ai import Task, task, eval
from inspect_ai.scorer import Metric, Score, Scorer, Target, mean, metric, scorer, match, Value
from inspect_ai.dataset import Dataset, Sample
import inspect_ai.dataset
from inspect_ai.solver import solver, Solver, generate, Generate, TaskState, multiple_choice, system_message
from inspect_ai.dataset import MemoryDataset
import tic_tac_toe
from inspect_ai.model import ChatMessageUser


SYSTEM_MESSAGE = """
Let's play a game of tic tac toe. Please make the best possible move to maximize your chances of winning and minimize your chances of losing. To make a move please enter a number between 0 and 8. The board is numbered as follows:

0 | 1 | 2
---------
3 | 4 | 5
---------
6 | 7 | 8
""".strip()

def add_user_message(state, message):
    state.messages.append(ChatMessageUser(content=message))

def parse_move(response: str) -> int:
    # response should be of the form "ANSWER: $NUMBER"
    assert response.startswith("ANSWER:"), f"Invalid response: {response}"
    move_str = response.split(":")[1].strip()
    assert move_str.isdigit(), f"Invalid move: {move_str}"
    return int(move_str)

@solver
def play_tic_tac_toe(opponent: tic_tac_toe.Bot) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        game = tic_tac_toe.TicTacToe()
        # todo: randomize player order

        
        message = ""
        while not game.winner:
            if game.current_player == 'X':
                # I think there's some sort of bug that changes the game state during search††
                move = opponent.get_move(game)
                message = game.current_player + f" plays at {move}" + "\n\n"
            else:
                # TODO
                message += game.board_to_string() + "\n\n" + game.current_player + " to move" + "Please enter a number between 0 and 8."
                add_user_message(state, message)

                state = await generate(state)
                response = state.messages[-1].content
                assert isinstance(response, str), f"Invalid response: {response}"
                move = parse_move(response)
                assert 0 <= move < 9, f"Invalid move: {move}"
            game.make_move(move)

            add_user_message(state, message)

        if game.winner == 'X':
            message = "Player wins!"
        elif game.winner == 'O':
            message = "Opponent wins!"
        elif game.winner == 'Tie':
            message = "Tie game!"
        else:
            raise ValueError(f"Invalid winner: {game.winner}")

        add_user_message(state, message)

        return state
        

    return solve

@scorer(metrics=[mean()])
def parse_score() -> Scorer:
    async def score(state: TaskState, target: Target) -> Score:
        last_message = state.messages[-1].content
        if last_message == "Player wins!":
            return Score(value=1)
        elif last_message == "Opponent wins!":
            return Score(value=0)
        elif last_message == "Tie game!":
            return Score(value=0.5)
        else:
            raise ValueError(f"Invalid message: {last_message}")
        
    return score

@task
def tic_tac_toe_eval(bot: tic_tac_toe.Bot, sys_message: str = "Let's play a game of tic tac toe.", num_games: int = 1000):
    dataset = MemoryDataset([Sample(input=str(i+1)) for i in range(num_games)])
    sys_message += "\n\n" + f"The entire content of your response should be of the following format: 'ANSWER: $NUMBER' (without quotes) where NUMBER is a number from 0 to 8."
    plan = [
        system_message(sys_message),
        play_tic_tac_toe(opponent=bot)
    ]
    scorer = parse_score()

    return Task(dataset, plan, scorer)


if __name__ == "__main__":
    model = "openai/gpt-3.5-turbo"
    bot = tic_tac_toe.TicTacToeBot('O', top_n=2)
    task = tic_tac_toe_eval(bot=bot, num_games=10)
    eval([task], model=model)