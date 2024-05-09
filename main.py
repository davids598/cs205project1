import heapq as q

class Node():
    def __init__(self) -> None:
        self.state = []
        self.parent = None
        self.depth = 0
        self.weight = None

    def setParent(self, parent):
        self.parent = parent

    def setState(self, state):
        self.state = state

    def setWeight(self, weight):
        self.weight = weight

    def setDepth(self, depth):
        self.depth = depth

    #This is necessary to work with the heap queue class in python that i am using
    def __lt__(self, node):
        return self.weight < node.weight

    def __gt__(self, node):
        return self.weight > node.weight

def readInput():
    print("Welcome to CS 205 Project 1, the 8-puzzle solver, by David Strathman (SID: 862170478).")
    print("Type \"1\" to use the default puzzle, or \"2\" to enter your own puzzle.")
    puzzle_choice = input()

    if puzzle_choice == "2":
        print("Enter your puzzle, use a space to represent the blank")
        print("Enter the first row, use no spaces between numbers")
        first_row = input()
        print("Enter the second row, use no spaces between numbers")
        second_row = input()
        print("Enter the third row, use no spaces between numbers")
        third_row = input()
        beginning_pos = []
        for x in first_row:
            beginning_pos.append(x)
        for x in second_row:
            beginning_pos.append(x)
        for x in third_row:
            beginning_pos.append(x)
    else:
        beginning_pos = ['1', '3', '6', '5', ' ', '2', '4', '7', '8']

    print("Select your choice of algorithm")
    print("(1) Uniform Cost Search\n(2) A* with Misplaced Tile Heuristic\n(3) A* with the Manhattan distance Heuristic")
    heuristic_choice = input()
    return beginning_pos, heuristic_choice

#Now begin the graph search, return a solution or failure
def search_puzzle(beginning_pos, heuristic_choice):
    num_nodes_expanded = 0
    max_queue_size = 0
    ROW_SIZE = 3
    COL_SIZE = 3
    goal_state = ['1', '2', '3', '4', '5', '6', '7', '8', ' ']
    frontier = [] #Will be used with q to be a priority queue
    #Set up root node
    node = Node()
    node.setState(beginning_pos)
    node.setWeight(0) 
    q.heappush(frontier, (node.weight, node)) #Set up min priority queue for frontier
    max_queue_size = 1
    explored_set = []

    while True:
        if len(frontier) == 0:
            print("Failure has occured")
        
        smallest_val = q.heappop(frontier)[1]
        num_nodes_expanded += 1
        #If node contains a goal state, then return the corresponding solution
        if smallest_val.state == goal_state:
            loop_node = smallest_val
            parent_list = []
            while loop_node.parent != None:
                parent_list.append(loop_node)
                loop_node = loop_node.parent
            parent_initial_state = Node()
            parent_initial_state.setState(beginning_pos)
            parent_list.append(parent_initial_state)
            parent_list.reverse()
            for x in parent_list:
                print(str(x.state) + "\n")
            print("Max queue size was " + str(max_queue_size) + "\nThe number of expanded nodes was " + str(num_nodes_expanded))
            print("Depth of goal state was " + str(smallest_val.depth))
            return
        #Add the node to the explored set
        state_list = []
        state_list = generate_states(smallest_val.state, ROW_SIZE, COL_SIZE)
        for x in state_list: #Expand the chosen node, adding the resulting nodes to the frontier (ONLY IF NOT IN THE FRONTIER OR EXPLORED SET)
            if x not in explored_set:
                node = Node()
                node.setState(x)
                node.setParent(smallest_val)
                node.setDepth(node.parent.depth + 1)
                node.setWeight(heuristicAlgo(node, heuristic_choice, goal_state, ROW_SIZE, COL_SIZE))
                explored_set.append(x)
                q.heappush(frontier, (node.weight, node))
        if max_queue_size < len(frontier):
            max_queue_size = len(frontier)

def heuristicAlgo(node, choice, correct, ROW_SIZE, COL_SIZE):
    #Uniform Cost Search (h(n) = 0)        f(n) = g(n) + h(n)
    curr_state = node.state
    if choice == "1":
        return node.depth

    #A* with misplaced tile heuristic
    elif choice == "2":
        count = 0
        for x in range(len(correct)):
            if curr_state[x] != correct[x] and correct[x] != " ":  # goal_state = ['1', '2', '3', '4', '5', '6', '7', '8', ' ']
                count += 1
        return count + node.depth

    #A* with Manhattan distance
    else:
        #weights equal to current node depth + all errors of every value within a particular state
        curr_depth_weight = node.depth
        #Now need to calculate errors for all elements in our state
        state_pos_error = 0
        #Replace space with 0 for searching
        curr_state_man = node.state.copy()
        index = curr_state_man.index(' ')
        curr_state_man[index] = '0'
        for i in range(len(correct)):
            if curr_state[i] != correct[i]:
                state_pos_error += calculateElementError(i, curr_state_man[i], ROW_SIZE, COL_SIZE)
        return curr_depth_weight + state_pos_error


def calculateElementError(i, valAtElement, ROW_SIZE, COL_SIZE):
    correct = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
    #Must find actual position of this element in the vector
    #Calculate distance between current position and proper position
    proper_pos = correct.index(valAtElement)
    
    #Location variable row and column
    curr_row = i / ROW_SIZE
    curr_col = i % COL_SIZE

    proper_pos_row = proper_pos % ROW_SIZE
    proper_pos_col = proper_pos / COL_SIZE

    x_axis_difference = abs(curr_col - proper_pos_col)
    y_axis_difference = abs(curr_row - proper_pos_row)

    return x_axis_difference + y_axis_difference

def generate_states(temp_pos, ROW_SIZE, COL_SIZE):
    curr_pos = temp_pos.copy()
    potential_states = []
    #Get the position of the blank for future checks
    index = curr_pos.index(' ')

    #Check if I can 'slide' a nearby tile into the blank, if such a position exists
    pullTop = False
    pullLeft = False
    pullRight = False
    pullBot = False

    if index >= ROW_SIZE:
        pullTop = True

    if (index <= (COL_SIZE * ROW_SIZE - 1 - ROW_SIZE)):
        pullBot = True

    if (index % ROW_SIZE != 0):
        pullLeft = True

    if (index % ROW_SIZE != (ROW_SIZE - 1)):
        pullRight = True

    #All these cases involving swapping the blank with a valid tile, putting that new state in the pot states array, then swapping back for the next check
    if pullTop:
        curr_pos[index - ROW_SIZE], curr_pos[index] = curr_pos[index], curr_pos[index - ROW_SIZE]
        potential_states.append(curr_pos.copy())
        curr_pos[index - ROW_SIZE], curr_pos[index] = curr_pos[index], curr_pos[index - ROW_SIZE]

    if pullLeft:
        curr_pos[index - 1], curr_pos[index] = curr_pos[index], curr_pos[index - 1]
        potential_states.append(curr_pos.copy())
        curr_pos[index - 1], curr_pos[index] = curr_pos[index], curr_pos[index - 1]

    if pullRight:
        curr_pos[index], curr_pos[index + 1] = curr_pos[index + 1], curr_pos[index]
        potential_states.append(curr_pos.copy())
        curr_pos[index], curr_pos[index + 1] = curr_pos[index + 1], curr_pos[index]

    if pullBot:
        curr_pos[index], curr_pos[index + ROW_SIZE] = curr_pos[index + ROW_SIZE], curr_pos[index]
        potential_states.append(curr_pos.copy())
        curr_pos[index], curr_pos[index + ROW_SIZE] = curr_pos[index + ROW_SIZE], curr_pos[index]

    return potential_states


if __name__ == '__main__':
    beginning_pos, heuristic_choice = readInput()
    search_puzzle(beginning_pos, heuristic_choice)
