import random
import time
from pathlib import Path

import streamlit as st


st.set_page_config(page_title="두더지 잡기 게임")

APP_DIR = Path(__file__).parent
HOLE_IMAGE = APP_DIR / "hole.png"
MOLE_IMAGE = APP_DIR / "img.png"
MOLE_DURATION_SECONDS = 1.5
REFRESH_SECONDS = 0.1
POINTS_PER_MOLE = 10
STARTING_LIVES = 3


def initialize_game_state():
    defaults = {
        "score": 0,
        "mole_id": 0,
        "mole_spawned_at": time.monotonic(),
        "last_processed_mole_id": -1,
        "lives": STARTING_LIVES,
        "game_over": False,
        "message": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if "mole_position" not in st.session_state:
        st.session_state.mole_position = None
        spawn_mole()


def spawn_mole():
    if st.session_state.game_over:
        return

    previous_position = st.session_state.mole_position
    available_holes = [
        index for index in range(9) if index != previous_position
    ]
    if previous_position is None:
        available_holes = list(range(9))
    st.session_state.mole_position = random.choice(available_holes)
    st.session_state.mole_id += 1
    st.session_state.mole_spawned_at = time.monotonic()


def resolve_mole(caught):
    if (
        st.session_state.game_over
        or st.session_state.mole_id <= st.session_state.last_processed_mole_id
    ):
        return

    st.session_state.last_processed_mole_id = st.session_state.mole_id
    if caught:
        st.session_state.score += POINTS_PER_MOLE
        st.session_state.message = "두더지를 잡았습니다!"
    else:
        st.session_state.lives = max(0, st.session_state.lives - 1)
        st.session_state.message = "시간이 지나 두더지를 놓쳤어요!"
        if st.session_state.lives == 0:
            st.session_state.game_over = True

    if st.session_state.game_over:
        st.rerun()
    spawn_mole()


def check_mole_timeout():
    if st.session_state.game_over:
        return False

    elapsed_seconds = time.monotonic() - st.session_state.mole_spawned_at
    if elapsed_seconds >= MOLE_DURATION_SECONDS:
        resolve_mole(caught=False)
        return True
    return False


def process_hole_click(hole_index, mole_id):
    if (
        st.session_state.game_over
        or mole_id != st.session_state.mole_id
        or mole_id <= st.session_state.last_processed_mole_id
    ):
        return

    if check_mole_timeout():
        return
    if hole_index == st.session_state.mole_position:
        resolve_mole(caught=True)


def render_game():
    st.write(f"라이프: {st.session_state.lives}")
    if st.session_state.game_over:
        st.error("게임 오버!")
        st.metric("최종 점수", st.session_state.score)
    else:
        st.metric("현재 점수", st.session_state.score)
        if st.session_state.message == "두더지를 잡았습니다!":
            st.success(st.session_state.message)
        elif st.session_state.message:
            st.warning(st.session_state.message)

    for row in range(3):
        columns = st.columns(3)
        for column in range(3):
            hole_index = row * 3 + column
            with columns[column]:
                image = (
                    MOLE_IMAGE
                    if not st.session_state.game_over
                    and hole_index == st.session_state.mole_position
                    else HOLE_IMAGE
                )
                st.image(str(image), width=160)
                st.button(
                    "구멍 클릭",
                    key=f"hole_{hole_index}",
                    on_click=process_hole_click,
                    args=(hole_index, st.session_state.mole_id),
                    width="stretch",
                    disabled=st.session_state.game_over,
                )


initialize_game_state()

st.title("두더지 잡기 게임")
st.subheader("두더지를 클릭해 보세요!")


@st.fragment(run_every=0.1 if not st.session_state.game_over else None)
def game_frame():
    check_mole_timeout()
    render_game()


game_frame()
