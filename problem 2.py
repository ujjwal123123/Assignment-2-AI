import enum


class bank_side(enum.Enum):
    Right = 1
    Left = 2


class State:
    def __init__(
        self,
        boat_location,
        parent=None,
        missionaries_right=3,
        cannibals_right=3,
        path_cost=0,
        depth=None,
    ):
        self.parent = parent
        self.boat_location = boat_location
        self.missionaries_right = missionaries_right
        self.cannibals_right = cannibals_right
        self.path_cost = path_cost
        self.depth = depth

    def __eq__(self, other):
        return (
            self.missionaries_right == other.missionaries_right
            and self.cannibals_right == other.cannibals_right
            and self.boat_location == other.boat_location
        )

    def __str__(self):
        return (
            f"The boat is on the {self.boat_location.name} side. "
            f"Path cost: {self.path_cost}. "
            f"\nOn right bank: {self.missionaries_right} missionaries and {self.cannibals_right} cannibals"
            f"\nOn left bank:  {3 - self.missionaries_right} missionaries and {3- self.cannibals_right} cannibals"
        )

    def __repr__(self):
        return f"({self.missionaries_right}, {self.cannibals_right}, {self.boat_location.name})"


def is_state_valid(missionaries_right, cannibals_right):
    """
    Called by generate_child_state so that it does not generate invalid states.
    """
    if missionaries_right > 3 or cannibals_right > 3:
        return False

    if missionaries_right < 0 or cannibals_right < 0:
        return False

    if missionaries_right != 0 and missionaries_right < cannibals_right:
        return False

    missionaries_left = 3 - missionaries_right
    cannibals_left = 3 - cannibals_right

    if missionaries_left != 0 and missionaries_left < cannibals_left:
        return False

    return True


def generate_child_state(parent):
    """
    Successor function
    """
    m_right = parent.missionaries_right
    c_right = parent.cannibals_right

    if parent.boat_location == bank_side.Right:
        # Boat on the right bank
        states = [
            (m_right - 1, c_right - 1),
            (m_right - 1, c_right),
            (m_right, c_right - 1),
            (m_right, c_right - 2),
            (m_right - 2, c_right),
        ]
    else:
        # Boat on the left bank
        states = [
            (m_right + 1, c_right + 1),
            (m_right + 1, c_right),
            (m_right, c_right + 1),
            (m_right, c_right + 2),
            (m_right + 2, c_right),
        ]

    child_boat_location = (
        bank_side.Right if parent.boat_location == bank_side.Left else bank_side.Left
    )

    child_depth = parent.depth + 1

    generated_states = []
    for state in states:
        if is_state_valid(*state):
            # Rs 10 for missionaries and Rs 20 for cannibals
            child_path_cost = (
                parent.path_cost
                + abs(m_right - state[0]) * 10
                + abs(c_right - state[1]) * 20
            )
            generated_states.append(
                State(
                    child_boat_location,
                    parent,
                    *state,
                    path_cost=child_path_cost,
                    depth=child_depth,
                )
            )

    return generated_states


def is_goal_state(state):
    return state.missionaries_right == 0 and state.cannibals_right == 0


def print_solution(state):
    print("Goal state:", state, sep="\n")

    print("\nPath:")
    stack = []
    while state:
        stack.append(state)
        state = state.parent

    while stack:
        state = stack.pop()
        print(state)
        print()

        if stack:
            child_boat_location = (
                bank_side.Right
                if state.boat_location == bank_side.Left
                else bank_side.Left
            )

            print(f"Moving boat to the {child_boat_location.name} side")
            print()


def bfs(initial_state):
    """
    Breath First Search

    Complete: Yes, if b is finite
    Optimal: Yes, if step costs are all identical
    """
    open_list = [initial_state]  # implemented as a queue
    closed_list = []

    while True:
        if not open_list:
            return None

        next_state = open_list.pop(0)
        closed_list.append(next_state)

        print("Expanding", repr(next_state))

        for child_state in generate_child_state(next_state):
            if child_state in closed_list or child_state in open_list:
                continue

            if is_goal_state(child_state):
                return child_state

            open_list.append(child_state)


def dfs(initial_state, depth_limit=None):
    """
    Depth First Search

    Complete: No
    Optimal: No

    This function also implements Depth Limited Search.
    """
    open_list = [initial_state]  # implemented as a stack
    closed_list = []

    cutoff_reached = False
    while True:
        if not open_list:
            if cutoff_reached:
                return None  # "Cutoff reached"
            else:
                return None  # "Failure"
            return None

        next_state = open_list.pop(-1)
        closed_list.append(next_state)

        if depth_limit is not None and next_state.depth >= depth_limit:
            cutoff_reached = True
            continue

        print("Expanding", repr(next_state))

        for child_state in generate_child_state(next_state):
            if child_state in closed_list or child_state in open_list:
                continue

            if is_goal_state(child_state):
                return child_state

            open_list.append(child_state)


def iterative_deepening(initial_state):
    """
    Iterative deepening search. Uses depth limited search algorithm whose
    implementation is provided by `dfs()`.

    NOTE: It does not return the optimal result for this problem
    NOTE: The function assumes that the solution is present.
    If the solution is not found, it will enter an infite loop.
    """
    depth = 0

    while True:
        ret = dfs(initial_state, depth)  # return value of the `dfs`
        print("Depth:", depth)
        if ret is not None:
            return ret

        depth += 1


def ucs(initial_state):
    """
    Uniform cost search
    Complete: Yes, if b is finite and step cost >= epsilon > 0
    Optimal: Yes
    """
    open_list = [initial_state]
    closed_list = []

    while True:
        if not open_list:
            return None

        min_cost_index = min(
            range(len(open_list)), key=lambda i: open_list[i].path_cost
        )
        next_state = open_list.pop(min_cost_index)
        closed_list.append(next_state)

        print("Expanding", repr(next_state))

        for child_state in generate_child_state(next_state):
            if child_state in closed_list or child_state in open_list:
                continue

            if is_goal_state(child_state):
                return child_state

            open_list.append(child_state)


if __name__ == "__main__":
    # generate initial state
    initial_state = State(bank_side.Right, None, 3, 3, 0, depth=0)

    print("***************************************************")
    print("                       BFS                         ")
    print("***************************************************")
    print_solution(bfs(initial_state))

    print()
    print("***************************************************")
    print("                       DFS                         ")
    print("***************************************************")
    print_solution(dfs(initial_state))

    print()
    print("***************************************************")
    print("                       IDS                         ")
    print("***************************************************")
    print_solution(iterative_deepening(initial_state))

    print()
    print("***************************************************")
    print("                       UCS                         ")
    print("***************************************************")
    print_solution(ucs(initial_state))
