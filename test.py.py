# Import color
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, SimpleDocTemplate

from utils import A4_height, A4_width, FrameComposite, add_circle, add_equidistant_lines, create_letter, create_matrix, dark_green_color, default_clause, get_division_positions, no_padding_frame_params, solid_green_line_params

print(A4)


margin_x_main = 10  # + A4_width % 1
margin_y_main = 50  # + A4_height % 1

print(
    f"Available width: {A4_width - margin_x_main}, Available height: {A4_height - margin_y_main}",
)


# PDF setup
pdf_file = "simple_form.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4)

# Get the sample stylesheet and create a custom ParagraphStyle. Left alignment is 0, right alignment is 2, and center alignment is 1.
styles = getSampleStyleSheet()
clause_style = ParagraphStyle(
    "Custom",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=5,
    leading=5,
    alignment=0,  # Justified text
    textColor=colors.darkgreen,
    spaceAfter=2,
    spaceBefore=0,
    firstLineIndent=5,
    hyphenationLang="de_DE",
    hyphenationMaxLines=2,
    hyphenationMinPrefix=0,
    hyphenationMinSuffix=0,
)


c = canvas.Canvas(pdf_file, pagesize=A4)
frame = FrameComposite(
    c,
    10,
    A4_width - 10,
    5,
    A4_height - 65,
    dark_green_color,
    2,
)

list_positions = [
    ((0, 9), (0, 20.0)),
    ((9, 59), (0, 3.5)),
    ((59, 100), (0, 3.5)),
]


frame_clause, frame_letter, frame_codes = create_matrix(c, frame, list_positions, {**solid_green_line_params, **no_padding_frame_params})

letter_width = frame_letter.frame_container.container_end_x - frame_letter.frame_container.container_start_x
letter_height = frame_letter.frame_container.container_end_y - frame_letter.frame_container.container_start_y


frame_clause.frame_container.frame.addFromList(
    [Paragraph(paragraph, style=clause_style) for paragraph in default_clause.split("<br/>")],
    c,
)

sizes_40_47 = np.array([7, 5, 5, 5])
dict_frames = {}

dict_frame_divisions = {
    # frame_num: [(divisions, offset)}]
    40: ((7, 0)),
    41: ((5, 0)),
    42: ((5, 0)),
    43: ((5, 0)),
    44: ((7, 0)),
    45: ((5, 0)),
    46: ((5, 0)),
    47: ((5, 0)),
}

list_positions = []

for row_idx in range(2):
    start_y = 100 * (0.5 * row_idx)
    end_y = 100 * (0.5 * (row_idx + 1))
    for col_idx, size in enumerate(sizes_40_47):
        start_x = 100 * sizes_40_47[:col_idx].sum() / sizes_40_47.sum()
        end_x = 100 * sizes_40_47[: col_idx + 1].sum() / sizes_40_47.sum()

        list_positions.append(
            ((start_x, end_x), (start_y, end_y)),
        )

frames_40_47 = create_matrix(c, frame_codes, list_positions, {**solid_green_line_params, **no_padding_frame_params})

for i, frame_iter in enumerate(frames_40_47):
    frame_num = 40 + i
    dict_frames[frame_num] = frame_iter

    add_equidistant_lines(frame_iter, c, sizes_40_47[i])


def fill_code_frame(canvas: canvas.Canvas, frame: FrameComposite, text: str, divisions: int):
    if len(text) != divisions:
        raise ValueError("Text must have the same number of characters as divisions")
    canvas.setFont("Courier", 7)
    y_start = frame.frame_container.container_start_y + 1
    center_positions = get_division_positions(frame, divisions)["center"]
    for j in range(len(text)):
        canvas.drawCentredString(center_positions[j], y_start, text[j])


# Duplicate sizes_40_47
sizes_40_47 = np.tile(sizes_40_47, 2)

for j, (frame_num, frame_iter) in enumerate(dict_frames.items()):
    divisions = sizes_40_47[j]
    print(divisions)
    fill_code_frame(c, frame_iter, "A" * divisions, divisions)

create_letter(c, frame_letter, **{**solid_green_line_params, **no_padding_frame_params})


add_circle(canvas=c, dict_frames=dict_frames, radius=3, color_background=colors.white, space=1, color_font=colors.darkgreen, color_stroke=colors.darkgreen)

dict_frames = {30: frame_letter}


list_positions = [
    ((9, 38), (3.5, 15)),  # 1
    ((38, 54.0), (3.5, 5.5)),  # 2
    ((38, 54.0), (5.5, 11.0)),  # 3
    ((9, 38), (11.0, 20.0)),  # 4
    ((38, 54.0), (11.0, 13.5)),  # 5
    ((38, 54.0), (13.5, 20.0)),  # 6
    ((54.0, 100), (3.5, 11.0)),  # 7
    ((75, 100), (3.5, 6.0)),  # 8
    ((54.0, 100), (11.0, 20.0)),  # 9
    ((0, 54.0), (20.0, 27.0)),  # 10
    ((19, 38), (20.0, 22.0)),  # 11
    ((38, 54.0), (20.0, 22.0)),  # 12
    ((0, 54.0), (27.0, 33.5)),  # 13
    ((34, 54.0), (27.0, 33.5)),  # 14
    ((0, 54.0), (33.5, 37.0)),  # 15
    ((54.0, 100), (20.0, 26.0)),  # 16
    ((82.0, 100), (20.0, 22.0)),  # 17
    ((54.0, 84.0), (26.0, 31.0)),  # 18
    ((84.0, 100), (26.0, 31.0)),  # 19
    ((54.0, 100), (31.0, 37.0)),  # 20
    ((0, 61.0), (37.0, 60.0)),  # 21
    ((33.5, 52.0), (37.0, 39.0)),  # 22
    ((52.0, 61.0), (37.0, 39.0)),  # 23
    ((61.0, 73.5), (37.0, 47.0)),  # 24
    ((73.5, 86.0), (37.0, 47.0)),  # 25
    ((86.0, 100.0), (37.0, 41.0)),  # 26
    ((86.0, 100.0), (41.0, 45.0)),  # 27
    ((86.0, 100.0), (45.0, 49.0)),  # 28
]

frames_1_28 = create_matrix(c, frame, list_positions, {**solid_green_line_params, **no_padding_frame_params})

for i, frame_iter in enumerate(frames_1_28):
    dict_frames.update({i + 1: frame_iter})

list_positions = [
    ((61.0, 86.0), (47.0, 60.0)),
    ((86.0, 100.0), (49.0, 60.0)),
]


frame_99, frame_48 = create_matrix(c, frame, list_positions, {**solid_green_line_params, **no_padding_frame_params})

dict_frames.update({48: frame_48, 99: frame_99})


abc_frame = create_matrix(c, frame, [((0, 54), (60, 80))], {**solid_green_line_params, **no_padding_frame_params})[0]


def create_letter_frame(canvas, letters="ABC", frame: FrameComposite = None):
    list_positions = []

    frame_width = frame.frame_container.container_end_x - frame.frame_container.container_start_x
    frame_height = frame.frame_container.container_end_y - frame.frame_container.container_start_y
    letter_frame_height = frame_height / len(letters)
    list_frames = []
    for i, letter in enumerate(letters):
        frame_letter = frame.add_frame(
            canvas=canvas,
            start_x=0,
            end_x=15,
            start_y=frame_height - letter_frame_height * i,
            end_y=frame_height - letter_frame_height * (i + 1),
            **{**solid_green_line_params, **no_padding_frame_params},
        )
        frame_letter_rest = frame.add_frame(
            canvas=canvas,
            start_x=15,
            end_x=frame_width,
            start_y=frame_height - letter_frame_height * i,
            end_y=frame_height - letter_frame_height * (i + 1),
            **{**solid_green_line_params, **no_padding_frame_params},
        )

        list_frames.append((frame_letter, frame_letter_rest))
    return list_frames


def split_letter_frames(canvas: canvas.Canvas, list_frames):
    list_split_frames = []
    for frame, frame_rest in list_frames:
        frame_1, frame_2 = create_matrix(
            canvas,
            frame_rest,
            [((0, 80), (0, 100)), ((80, 100), (0, 100))],
            {**solid_green_line_params, **no_padding_frame_params},
        )
        list_split_frames.append((frame_1, frame_2))
    return list_split_frames


def create_70_78(canvas, frame):
    list_positions = [
        ((0, 60), (100 - 0, 100 - 60)),
        ((60, 75), (100 - 0, 100 - 30)),
        ((75, 100), (100 - 0, 100 - 30)),
        ((60, 75), (100 - 30, 100 - 60)),
        ((75, 100), (100 - 30, 100 - 60)),
    ]

    return create_matrix(canvas, frame, list_positions, {**solid_green_line_params, **no_padding_frame_params})


def create_70_78(canvas, frame):
    list_positions = [
        ((0, 60), (100 - 0, 100 - 60)),
        ((60, 75), (100 - 0, 100 - 30)),
        ((75, 100), (100 - 0, 100 - 30)),
        ((60, 75), (100 - 30, 100 - 60)),
        ((75, 100), (100 - 30, 100 - 60)),
    ]

    return create_matrix(canvas, frame, list_positions, {**solid_green_line_params, **no_padding_frame_params})


letter_frames = create_letter_frame(c, "ABC", abc_frame)
list_split_frames = split_letter_frames(c, letter_frames)

for i, (frame_1, frame_2) in enumerate(list_split_frames):
    create_70_78(c, frame_1)


add_circle(canvas=c, dict_frames=dict_frames, radius=3, color_background=colors.darkgreen, space=1, color_font=colors.white, color_stroke=colors.darkgreen)

c.save()


treated_inputs = {
    40: "A" * 7,
    41: "A" * 5,
    42: "A" * 5,
    43: "A" * 5,
    44: "A" * 7,
    45: "A" * 5,
    46: "A" * 5,
    47: "A" * 5,
}
