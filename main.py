import streamlit as st
import chess
import chess.svg
import math
import random
import time
import html
import streamlit.components.v1 as components


# PAGE CONFIG
# Set up the main page details — title, layout, and overall structure
# ------------------------------------------------------------

st.set_page_config(
    page_title="Checkmate Intelligence — Chess AI",
    layout="wide",
)

# GLOBAL CSS - User Interface
# ------------------------------------------------------------

st.markdown(
    """
<style>
/* Page layout */
main.block-container {
    max-width: 1100px;
}

/* Board wrapper */
.board-wrapper {
    display: flex;
    justify-content: center;
    margin: 0 auto 10px auto;
}

/* Evaluation bar */
.evaluation-bar-outer {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: #111827;
    overflow: hidden;
    box-shadow: inset 0 0 4px rgba(0,0,0,0.5);
}
.evaluation-bar-inner {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #22c55e, #ef4444);
    transition: width 0.3s ease-out;
}

/* Move history container  */
.move-history-container {
    background: #111827;
    padding: 16px 18px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(15,23,42,0.9);
    color: #e5e7eb;
    max-height: 520px;
    overflow-y: auto;
}
.move-history-header {
    font-weight: 700;
    font-size: 1.05rem;
    margin-bottom: 10px;
    color: #00ffe0;
}
.mh-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.95rem;
}
.mh-table tr:nth-child(even) {
    background-color: rgba(255,255,255,0.03);
}
.mh-table tr:nth-child(odd) {
    background-color: rgba(0,0,0,0.25);
}
.mh-cell {
    padding: 6px 8px;
    color: #e5e7eb;
}
.mh-move-no {
    width: 14%;
    opacity: 0.7;
}
.mh-last {
    background-color: rgba(59,130,246,0.55) !important;
    font-weight: 700;
}

/* Headings */
h1, h2, h3 {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Segoe UI", sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: white;
    color: #e5e7eb;
}
</style>
""",
    unsafe_allow_html=True,
)


# Evaluation BAR
# ------------------------------------------------------------

def render_eval_bar(score):
    if score is None:
        score = 0
    try:
        score = float(score)
    except Exception:
        score = 0

    capped = max(min(score, 9999), -9999)
    percent = (capped + 9999) / 19998 * 100  # 0–100

    st.markdown(
        f"""
        <div class='evaluation-bar-outer'>
            <div class='evaluation-bar-inner' style='width:{percent}%;'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Evaluation function 
# ------------------------------------------------------------

def evaluate_board(board: chess.Board) -> float:
    # Terminal positions
  
    if board.is_checkmate():
        # If it's White to move in a checkmated position White has lost!!
        return -9999 if board.turn == chess.WHITE else 9999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

   
    # MATERIAL VALUES
    # ------------------------------------------------------------
    
    piece_values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }

    
    # PIECE-SQUARE TABLES
    # ------------------------------------------------------------
   
    pawn_table = [
         0,  5,  5, -10, -10,  5,  5,  0,
         0, 10, -5,   0,   0, -5, 10,  0,
         0, 10, 10,  20,  20, 10, 10,  0,
         5, 10, 10,  25,  25, 10, 10,  5,
        10, 15, 20,  30,  30, 20, 15, 10,
        20, 25, 25,  35,  35, 25, 25, 20,
        50, 50, 50,  50,  50, 50, 50, 50,
         0,  0,  0,   0,   0,  0,  0,  0,
    ]
    knight_table = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ]
    bishop_table = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ]
    rook_table = [
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  5, 10, 10,  5,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,
    ]
    queen_table = [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0,  0,
        -10,  0,  5,  5,  5,  5,  0,-10,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20,
    ]
    king_table = [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20,
        -10,-20,-20,-20,-20,-20,-20,-10,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -30,-40,-40,-50,-50,-40,-40,-30,
    ]

    piece_tables = {
        chess.PAWN: pawn_table,
        chess.KNIGHT: knight_table,
        chess.BISHOP: bishop_table,
        chess.ROOK: rook_table,
        chess.QUEEN: queen_table,
        chess.KING: king_table,
    }


    # King Safety
    # ------------------------------------------------------------
    
    phase = (
        (len(board.pieces(chess.QUEEN, chess.WHITE)) +
         len(board.pieces(chess.QUEEN, chess.BLACK))) * 2
        + (len(board.pieces(chess.ROOK, chess.WHITE)) +
           len(board.pieces(chess.ROOK, chess.BLACK)))
    )
    phase = min(phase / 16, 1.0)   # 1 ≈ opening/midgame, 0 ≈ endgame

    score = 0

    
    # Piece Loop 
    # ------------------------------------------------------------
   
    white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
    black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))

    for piece_type, val in piece_values.items():
        for square in board.pieces(piece_type, chess.WHITE):
            score += val
            score += piece_tables[piece_type][square] * 0.1

        for square in board.pieces(piece_type, chess.BLACK):
            score -= val
            score -= piece_tables[piece_type][chess.square_mirror(square)] * 0.1

    # Bishop pair bonus
    if white_bishops >= 2:
        score += 30
    if black_bishops >= 2:
        score -= 30

    # Mobility
    # ------------------------------------------------------------
    
    def side_mobility(bd: chess.Board, color: chess.Color) -> int:
        temp = bd.copy(stack=False)
        temp.turn = color
        return len(list(temp.legal_moves))

    white_mob = side_mobility(board, chess.WHITE)
    black_mob = side_mobility(board, chess.BLACK)
    score += (white_mob - black_mob) * 2

    # Pawn Structure
    # ------------------------------------------------------------
   
    def pawn_penalties(color: chess.Color) -> int:
        pawns = list(board.pieces(chess.PAWN, color))
        if not pawns:
            return 0
        files = [chess.square_file(p) for p in pawns]

        isolated = sum(
            1
            for f in files
            if (f - 1) not in files and (f + 1) not in files
        )
        doubled = len(pawns) - len(set(files))

        return isolated * 8 + doubled * 6

    score -= pawn_penalties(chess.WHITE)
    score += pawn_penalties(chess.BLACK)


    # King Safety Function
    # ------------------------------------------------------------

    def king_safety(color: chess.Color) -> float:
        king_sqs = list(board.pieces(chess.KING, color))
        if not king_sqs:
            return 0.0
        king_sq = king_sqs[0]
        rank = chess.square_rank(king_sq)
        file = chess.square_file(king_sq)

        # Distance from board centre (3.5, 3.5)
        dist_center = abs(rank - 3.5) + abs(file - 3.5)

        # Opening/middle: prefer being far from centre (castle)
        opening_penalty = (4 - dist_center) * phase * 8

        # Endgame: prefer being nearer the centre
        endgame_bonus = (4 - dist_center) * (1 - phase) * 8

        return opening_penalty - endgame_bonus

    score -= king_safety(chess.WHITE)
    score += king_safety(chess.BLACK)

    return score


# Board SVG 
# ------------------------------------------------------------

def make_board_svg(board: chess.Board, highlight_from=None) -> str:
    squares = None
    if highlight_from is not None:
        legal_targets = [
            m.to_square for m in board.legal_moves if m.from_square == highlight_from
        ]
        if legal_targets:
            squares = chess.SquareSet(legal_targets + [highlight_from])

    return chess.svg.board(
        board,
        size=520,
        coordinates=True,
        colors={"light": "#e5e9f0", "dark": "#0a1f33"},
        squares=squares,
    )


# MinMax Alpha Beta
# ------------------------------------------------------------

def minimax(board, depth, alpha, beta, maximizing_player, min_depth=1, max_depth=3):
    # Terminal node
    if board.is_game_over():
        return evaluate_board(board), None

    # Depth limit
    if depth >= max_depth:
        return evaluate_board(board), None

    # Early cutoff if position is already winning/losing
    current_eval = evaluate_board(board)
    if depth >= min_depth and abs(current_eval) > 5000:
        return current_eval, None

    best_move = None

    if maximizing_player:  # White node
        max_eval = -math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(
                board, depth + 1, alpha, beta, False, min_depth, max_depth
            )
            board.pop()

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move

    else:  # Black node
        min_eval = math.inf
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = minimax(
                board, depth + 1, alpha, beta, True, min_depth, max_depth
            )
            board.pop()

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move


# MCTS Monte Carlo tree search
# ------------------------------------------------------------
class MCTSNode:
    def __init__(self, board, parent=None, move=None):
        self.board = board.copy()
        self.parent = parent
        self.move = move
        self.children = {}              # move -> child node
        self.unexpanded_moves = list(board.legal_moves)
        self.visits = 0
        self.value = 0.0                # accumulated evaluation

    def is_fully_expanded(self):
        return len(self.unexpanded_moves) == 0

    def best_child(self, c_param=1.414):
        best_score = -math.inf
        best_child = None
        for move, child in self.children.items():
            exploitation = child.value / (child.visits + 1e-6)
            exploration = c_param * math.sqrt(
                math.log(self.visits + 1) / (child.visits + 1e-6)
            )
            score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

def rollout(board, depth):
    temp = board.copy()
    for _ in range(depth):
        if temp.is_game_over():
            break
        moves = list(temp.legal_moves)
        if not moves:
            break
        temp.push(random.choice(moves))
    score = evaluate_board(temp)
    # Scale result for more stable UCT values
    return float(score) / 1000.0

def backpropagate(node, result):
    while node is not None:
        node.visits += 1
        node.value += result
        result = -result          # switch perspective
        node = node.parent

def tree_policy(node):
    while not node.board.is_game_over():
        if node.unexpanded_moves:
            move = node.unexpanded_moves.pop()
            new_board = node.board.copy()
            new_board.push(move)
            child = MCTSNode(new_board, parent=node, move=move)
            node.children[move] = child
            return child
        node = node.best_child()
    return node

def mcts_ai(board, sims=30, playout_depth=3):
    root = MCTSNode(board)

    if not list(board.legal_moves):
        return None

    for _ in range(sims):
        leaf = tree_policy(root)
        result = rollout(leaf.board, playout_depth)

        # normalize perspective root side-to-move as maximizing
        if not board.turn:
            result = -result

        backpropagate(leaf, result)

    if not root.children:
        return None

    # Choosing the child visited the most
    best_move = max(root.children.items(), key=lambda item: item[1].visits)[0]
    return best_move


# Sarsa State-Action-Reward-State-Action
# ------------------------------------------------------------

if "sarsa_Q" not in st.session_state:
    st.session_state.sarsa_Q = {}

def sarsa_ai(board: chess.Board, alpha=0.1, gamma=0.9, epsilon=0.2):
    
    Q = st.session_state.sarsa_Q

    state = board.fen()
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    # greedy action selection
    if random.random() < epsilon:
        move = random.choice(legal_moves)
    else:
        move = max(legal_moves, key=lambda m: Q.get((state, m.uci()), 0.0))

    # simulating and taking the move
    board.push(move)
    reward = evaluate_board(board) / 1000.0
    next_state = board.fen()

    next_legal = list(board.legal_moves)
    if not next_legal or board.is_game_over():
        next_q = 0.0
    else:
        # Greedy next action for SARSA update
        next_move = max(next_legal, key=lambda m: Q.get((next_state, m.uci()), 0.0))
        next_q = Q.get((next_state, next_move.uci()), 0.0)

    prev_q = Q.get((state, move.uci()), 0.0)
    Q[(state, move.uci())] = prev_q + alpha * (reward + gamma * next_q - prev_q)

    # reverting board to original state before returning move
    board.pop()
    return move

# General ai dispatch

def choose_ai_move(agent_name: str, board: chess.Board, depth: int, mcts_sims: int | None):
    if agent_name == "Minimax":
        maximizing = board.turn == chess.WHITE
        _, move = minimax(
            board,
            depth=0,  # start from 0 so plies label is accurate
            alpha=-math.inf,
            beta=math.inf,
            maximizing_player=maximizing,
            min_depth=1,
            max_depth=depth,
        )
        return move
    elif agent_name == "MCTS":
        sims = mcts_sims or 50
        return mcts_ai(board.copy(), sims=sims, playout_depth=depth)
    elif agent_name == "SARSA":
        return sarsa_ai(board)
    else:
        return None


# Move History
# ------------------------------------------------------------
def safe(s):
    return html.escape(s)

def move_history_table(moves, title="Move History"):
    html_code = f"""<div class="move-history-container">
  <div class="move-history-header">♟ {title}</div>
  <table class="mh-table">
"""
    for i in range(0, len(moves), 2):
        move_no = i // 2 + 1
        white_mv = safe(moves[i])
        black_mv = safe(moves[i + 1]) if i + 1 < len(moves) else ""
        is_last_row = (i >= len(moves) - 2)
        last_class = "mh-last" if is_last_row else ""

        html_code += f"""
    <tr class="{last_class}">
        <td class="mh-cell mh-move-no">{move_no}</td>
        <td class="mh-cell">{white_mv}</td>
        <td class="mh-cell">{black_mv}</td>
    </tr>
"""
    html_code += """
  </table>
</div>
"""
    return html_code


# Streamlit app switch
# ------------------------------------------------------------
st.markdown("<h1>Chess Project — Human vs AI & AI vs AI</h1>", unsafe_allow_html=True)
mode = st.radio("Choose Mode:", ["Human vs AI", "AI vs AI Battle"])


# Human vs Ai
# ============================================================
if mode == "Human vs AI":

    st.sidebar.subheader("Human vs AI Settings")
    ai_choice = st.sidebar.selectbox("AI Agent:", ("Minimax", "MCTS", "SARSA"))
    depth_choice = st.sidebar.selectbox("Search depth (plies):", [1, 3, 5], index=1)

    player_color = st.sidebar.radio("Play as:", ("White", "Black"))
    player_is_white = (player_color == "White")

    mcts_sims = None
    if ai_choice == "MCTS":
        mcts_sims = st.sidebar.slider("MCTS: Simulation Count", 10, 200, 50, step=10)

    # Reseting a board when settings change
    config_tuple = (ai_choice, depth_choice, player_color)

    if "hvai_config" not in st.session_state:
        # First time initialization
        st.session_state.hvai_config = config_tuple
        st.session_state.board = chess.Board()
        st.session_state.history = []
        st.session_state.awaiting_ai = False
        st.session_state.ai_started = False
    elif st.session_state.hvai_config != config_tuple:
        # Config changed will be reset game
        st.session_state.hvai_config = config_tuple
        st.session_state.board = chess.Board()
        st.session_state.history = []
        st.session_state.awaiting_ai = False
        st.session_state.ai_started = False

    board = st.session_state.board

    # If player chose Black AI (White) moves first
    if (not player_is_white) and (not st.session_state.ai_started) and not board.is_game_over():
        first_move = choose_ai_move(ai_choice, board, depth_choice, mcts_sims)
        if first_move and first_move in board.legal_moves:
            san = board.san(first_move)
            board.push(first_move)
            st.session_state.history.append(san)
        st.session_state.ai_started = True

    # Layout: board + controls left, history right
    col1, spacer, col2 = st.columns([2, 0.15, 1])

    #LEFT: Board & Input 
    # ------------------------------------------------------------
    with col1:
        st.markdown("Game Board")

        highlight_sq_text = st.text_input(
            "Highlight moves from square (e.g. e2):",
            key="highlight_sq",
        )
        highlight_sq = None
        if highlight_sq_text:
            try:
                highlight_sq = chess.parse_square(highlight_sq_text.strip().lower())
            except ValueError:
                st.warning("Use coordinates like e2, d4, etc.")
                highlight_sq = None

        board_svg = make_board_svg(board, highlight_from=highlight_sq)
        st.markdown("<div class='board-wrapper'>", unsafe_allow_html=True)
        st.write(board_svg, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Evaluation bar
        score = evaluate_board(board)
        st.markdown("Position Evaluation")
        render_eval_bar(score)
        st.caption(f"Score (White – Black): {score:.2f}")

        # Move Input
        st.markdown("Enter Move")
        move_input = st.text_input("UCI format (e.g. e2e4):", key="move_input")

        btn_col, _ = st.columns([1, 3])
        with btn_col:
            make_move_btn = st.button("Click twice to make Move", use_container_width=True)

        #HUMAN MOVE
        # ------------------------------------------------------------
        if make_move_btn and not board.is_game_over():
            try:
                raw = move_input.strip().replace(" ", "").lower()
                user_move = chess.Move.from_uci(raw)

                human_turn = (
                    (board.turn and player_is_white) or
                    ((not board.turn) and (not player_is_white))
                )

                if not human_turn:
                    st.error("It's not your turn!")
                elif user_move in board.legal_moves:
                    san = board.san(user_move)
                    board.push(user_move)
                    st.session_state.history.append(san)

                    st.session_state.awaiting_ai = (
                        (board.turn and not player_is_white) or
                        ((not board.turn) and player_is_white)
                    )
                else:
                    st.error("Illegal move! Try again.")
            except Exception as e:
                st.error(f"Invalid input: {e}")

        # AI MOVE 
        # ------------------------------------------------------------
        if st.session_state.awaiting_ai and not board.is_game_over():
            with st.spinner("🤖 AI is thinking..."):
                ai_move = choose_ai_move(ai_choice, board, depth_choice, mcts_sims)

                if ai_move and ai_move in board.legal_moves:
                    ai_san = board.san(ai_move)
                    board.push(ai_move)
                    st.session_state.history.append(ai_san)
                else:
                    st.error("AI generated an illegal move!")

                st.session_state.awaiting_ai = False

        #  GAME END 
        # ------------------------------------------------------------
        if board.is_game_over():
            result = board.result()
            if result == "1-0":
                st.success("White wins — Checkmate or resignation!")
            elif result == "0-1":
                st.error("Black wins — Checkmate or resignation!")
            else:
                st.warning("Drawn game.")
            st.session_state.awaiting_ai = False

    # RIGHT: Move History 
    # ------------------------------------------------------------
    with col2:
        st.markdown("Game Feed")
        san_moves = st.session_state.history
        history_html = move_history_table(san_moves, title="Move History")

        # Render as a pure HTML component (no Markdown parsing)
        components.html(history_html, height=520, scrolling=True)


# AI vs AI Battle
# ------------------------------------------------------------
else:
    st.subheader(" AI vs AI Battle Arena")

    ai_pair = st.selectbox(
        "Select AIs to Compete:",
        ["Minimax vs MCTS", "SARSA vs MCTS", "Minimax vs SARSA"],
    )

    # One speed slider game will always runs until checkmate/draw
    speed = st.slider("Move Delay (seconds)", 0.1, 2.0, 0.5, key="battle_speed")

    st.sidebar.subheader("AI vs AI Settings")
    depth_battle = st.sidebar.selectbox("Search depth (plies):", [1, 3, 5], index=1)
    sims_battle = st.sidebar.slider("MCTS: Simulation Count", 10, 200, 50, step=10)

    # Session_state to keep board & moves between reruns
    if "ai_board" not in st.session_state:
        st.session_state.ai_board = chess.Board()
        st.session_state.ai_moves = []

    board = st.session_state.ai_board
    moves = st.session_state.ai_moves

    board_placeholder = st.empty()
    history_placeholder = st.empty()

    if st.button("Start Battle"):
        # Reset board & history for new game
        st.session_state.ai_board = chess.Board()
        st.session_state.ai_moves = []
        board = st.session_state.ai_board
        moves = st.session_state.ai_moves

        # Decide which AI is White / Black for THIS battle
        base_white, base_black = ai_pair.split(" vs ")
        if random.choice([True, False]):
            white_ai, black_ai = base_white, base_black
        else:
            white_ai, black_ai = base_black, base_white

        st.info(f"Randomized colors: {white_ai} plays White, {black_ai} plays Black")

        # MAIN BATTLE LOOP run until checkmate/draw 
        while not board.is_game_over():
            if board.turn:    # White to move
                move = choose_ai_move(white_ai, board, depth_battle, sims_battle)
            else:             # Black to move
                move = choose_ai_move(black_ai, board, depth_battle, sims_battle)

            # Safety: if AI gives illegal/None, fall back to random legal move
            if move is None or move not in board.legal_moves:
                move = random.choice(list(board.legal_moves))

            san = board.san(move)
            board.push(move)
            moves.append(san)

            # Update board display
            svg = chess.svg.board(board, size=400)
            board_placeholder.markdown(
                f"<div style='display:flex; justify-content:center;'>{svg}</div>",
                unsafe_allow_html=True,
            )

            history_placeholder.html(move_history_table(moves))

            # Just for visual speed so user can see the moves in easy way 
            time.sleep(speed)

        # Game over & evaluation
        result = board.result()
        final_eval = evaluate_board(board)

        if result == "1-0":
            st.success(f"Checkmate! White ({white_ai}) wins.")
        elif result == "0-1":
            st.error(f"Checkmate! Black ({black_ai}) wins.")
        else:
            st.warning("Game ended in a draw.")

        if final_eval > 300:
            st.write(f"Evaluation suggests White ({white_ai}) was dominating.")
        elif final_eval < -300:
            st.write(f"Evaluation suggests Black ({black_ai}) was dominating.")
        elif -50 <= final_eval <= 50:
            st.write("Evaluation: Completely equal game.")
        else:
            st.write("Evaluation: Slight edge but close game.")
