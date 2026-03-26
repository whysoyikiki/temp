import io
from typing import Dict, Optional

import streamlit as st
from PIL import Image


st.set_page_config(page_title="표 생성기", layout="wide")

st.title("표 생성기")
st.caption("가로/세로 칸 수를 지정하고, 상단 텍스트와 좌측 이미지를 넣을 수 있습니다.")


# ------------------------------
# 상태 초기화
# ------------------------------
if "grid_created" not in st.session_state:
    st.session_state.grid_created = False
if "cols" not in st.session_state:
    st.session_state.cols = 3
if "rows" not in st.session_state:
    st.session_state.rows = 3
if "header_texts" not in st.session_state:
    st.session_state.header_texts = {}
if "row_images" not in st.session_state:
    st.session_state.row_images = {}
if "row_image_widths" not in st.session_state:
    st.session_state.row_image_widths = {}


# ------------------------------
# 표 설정
# ------------------------------
with st.sidebar:
    st.header("표 설정")
    cols = st.number_input("가로 칸 수", min_value=1, max_value=20, value=st.session_state.cols, step=1)
    rows = st.number_input("세로 칸 수", min_value=1, max_value=20, value=st.session_state.rows, step=1)

    if st.button("표 생성 / 갱신", use_container_width=True):
        st.session_state.cols = int(cols)
        st.session_state.rows = int(rows)
        st.session_state.grid_created = True

        # 기존 키가 범위를 벗어나면 정리
        st.session_state.header_texts = {
            k: v for k, v in st.session_state.header_texts.items() if k < st.session_state.cols
        }
        st.session_state.row_images = {
            k: v for k, v in st.session_state.row_images.items() if k < st.session_state.rows
        }
        st.session_state.row_image_widths = {
            k: v for k, v in st.session_state.row_image_widths.items() if k < st.session_state.rows
        }


if not st.session_state.grid_created:
    st.info("왼쪽 사이드바에서 가로/세로 칸 수를 정한 뒤 '표 생성 / 갱신'을 눌러주세요.")
    st.stop()


cols = st.session_state.cols
rows = st.session_state.rows


# ------------------------------
# 상단 헤더 입력
# ------------------------------
st.subheader("1) 가장 윗칸 텍스트 입력")
header_cols = st.columns(cols)
for c in range(cols):
    current = st.session_state.header_texts.get(c, "")
    value = header_cols[c].text_input(
        f"상단 {c+1}열 텍스트",
        value=current,
        key=f"header_input_{c}",
    )
    st.session_state.header_texts[c] = value

st.divider()


# ------------------------------
# 좌측 이미지 업로드 + 크기 조절
# ------------------------------
st.subheader("2) 좌측 행 이미지 업로드")
for r in range(rows):
    with st.expander(f"{r+1}행 이미지 설정", expanded=False):
        uploaded = st.file_uploader(
            f"{r+1}행 이미지 업로드",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"uploader_{r}",
        )

        if uploaded is not None:
            image_bytes = uploaded.getvalue()
            st.session_state.row_images[r] = image_bytes

        width_default = st.session_state.row_image_widths.get(r, 120)
        new_width = st.slider(
            f"{r+1}행 이미지 너비(px)",
            min_value=50,
            max_value=400,
            value=width_default,
            step=10,
            key=f"width_slider_{r}",
        )
        st.session_state.row_image_widths[r] = new_width

        if r in st.session_state.row_images:
            preview = Image.open(io.BytesIO(st.session_state.row_images[r]))
            st.image(preview, width=new_width, caption=f"{r+1}행 미리보기")
        else:
            st.caption("아직 업로드된 이미지가 없습니다.")

st.divider()


# ------------------------------
# 최종 표 미리보기
# ------------------------------
st.subheader("3) 표 미리보기")

# 표 전체는 (rows + 1) x (cols + 1)
# [0,0]은 빈칸
# 첫 행: 상단 헤더
# 첫 열: 좌측 이미지
for rr in range(rows + 1):
    line = st.columns(cols + 1)

    for cc in range(cols + 1):
        with line[cc]:
            # 좌상단 빈칸
            if rr == 0 and cc == 0:
                st.markdown(
                    "<div style='height:70px; border:1px solid #d9d9d9; border-radius:8px;'></div>",
                    unsafe_allow_html=True,
                )

            # 상단 헤더
            elif rr == 0 and cc > 0:
                text = st.session_state.header_texts.get(cc - 1, "")
                st.markdown(
                    f"""
                    <div style='
                        min-height:70px;
                        border:1px solid #d9d9d9;
                        border-radius:8px;
                        padding:10px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        text-align:center;
                        font-weight:600;
                    '>{text if text else '&nbsp;'}</div>
                    """,
                    unsafe_allow_html=True,
                )

            # 좌측 이미지 셀
            elif rr > 0 and cc == 0:
                st.markdown(
                    "<div style='padding:6px; border:1px solid #d9d9d9; border-radius:8px; min-height:120px;'>",
                    unsafe_allow_html=True,
                )
                if (rr - 1) in st.session_state.row_images:
                    img = Image.open(io.BytesIO(st.session_state.row_images[rr - 1]))
                    width = st.session_state.row_image_widths.get(rr - 1, 120)
                    st.image(img, width=width)
                else:
                    st.caption("이미지 없음")
                st.markdown("</div>", unsafe_allow_html=True)

            # 일반 셀
            else:
                st.markdown(
                    "<div style='min-height:120px; border:1px solid #d9d9d9; border-radius:8px;'></div>",
                    unsafe_allow_html=True,
                )


st.divider()
st.subheader("실행 방법")
st.code("pip install streamlit pillow\nstreamlit run streamlit_table_app.py", language="bash")
