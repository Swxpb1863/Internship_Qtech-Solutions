import random
import math

class treeNode():
    def __init__(self, board, parent):
        self.board = board

        if self.board.is_win() or self.board.is_draw():
            self.Terminal = True
        else:
            self.Terminal = False
        
        self.is_fully_expanded = self.Terminal 
        self.parent = parent
        self.visits = 0
        self.score = 0
        self.children = {}

class MCTS():
    def search(self, initial_state):
        self.root = treeNode(initial_state, None)

        for iteration in range(800):
            node = self.select(self.root)
            score = self.rollout(node.board)

            self.backpropagate(node, score)
        
        try:
            return self.get_best_move(self.root, 0)
        except:
            pass
    
    def select(self, node):
        while not node.Terminal:
            if node.is_fully_expanded:
                node = self.get_best_move(node, 2)
            else:
                return self.expand(node)
        return node
    
    def expand(self, node):
        states = node.board.generate_states()

        for state in states:
            if str(state.position) not in node.children:
                new_Node = treeNode(state, node)
                node.children[str(state.position)] = new_Node
            
                if len(states) == len(node.children):
                    node.is_fully_expanded = True
                return new_Node

        print("Should not come here!!")



    def rollout(self, board):
        while not board.is_win():
            try:
                board = random.choice(board.generate_states())
            except:
                return 0
        
        if board.player_2 == 'x': return 1
        elif board.player_2 == 'o': return -1 


    def backpropagate(self, node, score):
        while node is not None:
            node.visits += 1

            node.score += score
            node = node.parent


    def get_best_move(self, node, exploration_constant):
        best_score = float('-inf')
        best_moves = []

        for child_node in node.children.values():
            if child_node.board.player_2 == 'x' : current_player = 1
            elif child_node.board.player_2 == 'o' : current_player = -1

            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(math.log(node.visits/child_node.visits))

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]
            
            elif move_score == best_score:
                best_moves.append(child_node)

        return random.choice(best_moves)