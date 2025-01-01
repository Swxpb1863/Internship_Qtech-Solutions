import streamlit as st
import time
from mcts import *
import numpy as np
import pandas as pd
from copy import deepcopy

class Board():
    def __init__(self, board=None):
        self.player_1 = 'x'
        self.player_2 = 'o'
        self.empty_square = '~'
        self.position = {}
        self.init_board()
        if board is not None:
            self.__dict__ = deepcopy(board.__dict__)

    def init_board(self):
        for row in range(3):
            for col in range(3):
                self.position[row, col] = self.empty_square

    def make_move(self, row, col):
        board = Board(self)
        board.position[row, col] = self.player_1
        (board.player_1, board.player_2) = (board.player_2, board.player_1)
        return board

    def is_draw(self):
        for row, col in self.position:
            if self.position[row, col] == self.empty_square:
                return False
        return True

    def is_win(self):
        for col in range(3):
            if all(self.position[row, col] == self.player_2 for row in range(3)):
                return True
        for row in range(3):
            if all(self.position[row, col] == self.player_2 for col in range(3)):
                return True
        if all(self.position[i, i] == self.player_2 for i in range(3)):
            return True
        if all(self.position[i, 2 - i] == self.player_2 for i in range(3)):
            return True
        return False

    def generate_states(self):
        actions = []
        for row in range(3):
            for col in range(3):
                if self.position[row, col] == self.empty_square:
                    actions.append(self.make_move(row, col))
        return actions

def main():
    st.title("Tic Tac Toe Game - AI vs Human")
    if "play_first" not in st.session_state:
        st.session_state.play_first = None

    # Page 1: Ask if the user wants to play first
    if st.session_state.play_first is None:
        st.write("Would you like to play first? First player plays as X.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes"):
                initialize_game(True)
        with col2:
            if st.button("No"):
                initialize_game(False)

    # Page 2: Tic Tac Toe game
    if st.session_state.play_first is not None:
        game_board()

def initialize_game(play_first):
    # Initialize game state based on the user's choice
    st.session_state.play_first = play_first
    st.session_state.user_symbol = 'x' if play_first else 'o'
    st.session_state.ai_symbol = 'o' if play_first else 'x'
    st.session_state.board = Board()
    st.session_state.current_player = st.session_state.user_symbol

    if not play_first:  # AI makes the first move if the user doesn't want to play first
        ai_first_move()

def ai_first_move():
    # AI makes the first move
    mcts = MCTS()
    best_move = mcts.search(st.session_state.board)
    st.session_state.board = best_move.board
    st.session_state.current_player = st.session_state.user_symbol  # Switch to user's turn

def game_board():
    # Display the game board
    board_placeholder = st.empty()
    status_placeholder = st.empty()
    
    st.markdown("""
        <style>
            .tic-tac-toe-table {
                width: 150px;  /* Adjust the width */
                height: 80px; /* Adjust the height */
                font-size: 25px; /* Adjust the font size of the table */
            }
            .tic-tac-toe-table td {
                border: 1px solid black;
                text-align: center; /* Optional: add border */
            }
        </style>
        """, unsafe_allow_html=True)

    # Modify your table rendering code to use the custom class
    def display_board():
        board = st.session_state.board
        board_table = [board.position[row, col] for row in range(3) for col in range(3)]
        df_board = pd.DataFrame(np.array(board_table).reshape(3, 3))
        table_html = df_board.to_html(classes='tic-tac-toe-table', header=False, index=False)
        board_placeholder.markdown(table_html, unsafe_allow_html=True)
    display_board()

    # Handle user's turn
    if st.session_state.current_player == st.session_state.user_symbol:
        status_placeholder.text("Your turn! Choose a square and press 'Play' to confirm.")
        st.session_state.selected_cell = st.selectbox("Choose a cell (1-9):", range(1, 10))
        if st.button("Play"):
            row = (st.session_state.selected_cell - 1) // 3
            col = (st.session_state.selected_cell - 1) % 3

            if st.session_state.board.position[row, col] == st.session_state.board.empty_square:
                st.session_state.board = st.session_state.board.make_move(row, col)
                display_board()
                if st.session_state.board.is_win():
                    status_placeholder.success("You win!")
                    st.button("Play Again", on_click=reset_game)
                    st.stop()
                elif st.session_state.board.is_draw():
                    status_placeholder.info("It's a draw!")
                    st.button("Play Again", on_click=reset_game)
                    st.stop()
                else:
                    st.session_state.current_player = st.session_state.ai_symbol
            else:
                st.warning('Illegal Move! Please try a different square.', icon="⚠️")

    # Handle AI's turn
    if st.session_state.current_player == st.session_state.ai_symbol:
        status_placeholder.text("AI's turn...")
        time.sleep(3)  # Simulate AI thinking for 3 seconds
        mcts = MCTS()
        best_move = mcts.search(st.session_state.board)
        st.session_state.board = best_move.board
        display_board()
        if st.session_state.board.is_win():
            status_placeholder.success("AI wins!")
            st.button("Play Again", on_click=reset_game)
            st.stop()
        elif st.session_state.board.is_draw():
            status_placeholder.info("It's a draw!")
            st.button("Play Again", on_click=reset_game)
            st.stop()
        else:
            st.session_state.current_player = st.session_state.user_symbol  # Switch back to user's turn
            status_placeholder.text("Your turn! Choose a square and press 'Play' to confirm.")

def reset_game():
    st.session_state.play_first = None
    st.session_state.user_symbol = None
    st.session_state.ai_symbol = None
    st.session_state.board = None
    st.session_state.current_player = None
    st.session_state.selected_cell = None

if __name__ == "__main__":
    main()
