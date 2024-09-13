# Import color
from typing import Any, Tuple

import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Frame, Paragraph, SimpleDocTemplate

A4_width, A4_height = A4
styles = getSampleStyleSheet()
dark_green_color = (4 / 255, 145 / 255, 103 / 255)

no_padding_frame_params = {"leftPadding": 0, "topPadding": 0, "rightPadding": 0, "bottomPadding": 0}

solid_green_line_params = {"stroke_color": dark_green_color, "stroke_width": 1, "fill": 0}
transparent_frame_params = {"stroke_color": colors.white, "stroke_width": 0, "fill": 0}
solid_black_line_params = {"stroke_color": (0, 0, 0), "stroke_width": 1, "fill": 0}


def create_line(canvas, start_x, end_x, start_y, end_y, color, width):
    canvas.setStrokeColor(color)
    canvas.setLineWidth(width)
    canvas.line(start_x, start_y, end_x, end_y)


def draw_rectangle(
    canvas: canvas.Canvas,
    x_start: float,
    x_end: float,
    y_start: float,
    y_end: float,
    stroke_color: tuple[float, float, float],
    stroke_width: int,
    fill: int = 0,
) -> None:
    canvas.setStrokeColorRGB(*stroke_color)
    canvas.setLineWidth(stroke_width)
    canvas.rect(
        x_start,
        y_start,
        x_end - x_start,
        y_end - y_start,
        stroke=1,
        fill=fill,
    )


class FrameContainer:
    def __init__(self, canvas, start_x, end_x, start_y, end_y, stroke_color, stroke_width, fill=0, **kwargs) -> None:
        self.container_start_x = start_x
        self.container_end_x = end_x
        self.container_start_y = start_y
        self.container_end_y = end_y
        self.container_center_x = (start_x + end_x) / 2
        self.container_center_y = (start_y + end_y) / 2

        self.frame = Frame(
            start_x,
            start_y,
            abs(end_x - start_x),
            abs(end_y - start_y),
            **kwargs,
        )

        if (fill > 0) or (stroke_width > 0):
            draw_rectangle(
                canvas,
                start_x,
                end_x,
                start_y,
                end_y,
                stroke_color,
                stroke_width,
                fill,
            )


class FrameComposite:
    def __init__(self, canvas: canvas.Canvas, start_x, end_x, start_y, end_y, stroke_color, stroke_width, fill=0, **kwargs) -> None:
        self.start_x = start_x
        self.end_x = end_x

        self.start_y = A4_height - end_y
        self.end_y = A4_height - start_y
        self.text_fields = []
        self.canvas = canvas
        self.frame_container = FrameContainer(
            canvas,
            start_x,
            end_x,
            start_y,
            end_y,
            stroke_color,
            stroke_width,
            fill,
            **kwargs,
        )

    def add_text_field(self, **kwargs):
        type_field = kwargs["type_field"]
        if type_field == "frame_code":
            divisions = kwargs["divisions"]
            position = kwargs.get("position", ((0, 100), (0, 100)))
            frame = create_matrix(self.canvas, self, [position], **{**solid_green_line_params, **no_padding_frame_params})[0]

            self.text_fields.append({"type_field": type_field, "frame": frame, "divisions": divisions})

    def fill_text_field(self, idx: int, value, **kwargs: dict[str, Any]):
        font_params = kwargs.get("font_params", {"font": "Courier", "size": 7})
        self.canvas.setFont(**font_params)

        type_field = self.text_fields[idx]["type_field"]
        if type_field == "frame_code":
            if len(value) != self.text_fields[idx]["divisions"]:
                raise ValueError(f"Text length must be equal to number of divisions. Got {len(value)} and {self.text_fields[idx]['divisions']}")

            offset_y = kwargs.get("offset_y", 1)
            frame: FrameComposite = self.text_fields[idx]["frame"]

            divisions = self.text_fields[idx]["divisions"]
            center_positions = get_division_positions(frame, divisions)["center"]

            for j in range(len(value)):
                frame.canvas.drawCentredString(center_positions[j], frame.frame_container.container_start_y + offset_y, value[j], mode=0)

    def fill_text_fields(self, values: list[tuple[str, dict]]):
        for idx, (value, kwargs) in enumerate(values):
            self.fill_text_field(idx, value, **kwargs)

    def add_frame(self, canvas, start_x, end_x, start_y, end_y, stroke_color, stroke_width, fill=0, **kwargs):
        start_x += self.start_x
        end_x += self.start_x

        start_y_reversed = A4_height - self.start_y - end_y
        end_y_reversed = A4_height - self.start_y - start_y

        frame = FrameComposite(canvas, start_x, end_x, start_y_reversed, end_y_reversed, stroke_color, stroke_width, fill, **kwargs)
        return frame


def add_circle(
    canvas: canvas.Canvas,
    dict_frames: dict[int, FrameComposite],
    radius,
    color_background,
    space=0.5,
    color_font=colors.white,
    color_stroke=colors.darkgreen,
) -> None:
    # Add circle
    canvas.setLineWidth(1)
    for num, frame_with_circle in dict_frames.items():
        canvas.setFillColor(color_background)
        canvas.setStrokeColor(color_stroke)
        canvas.circle(
            frame_with_circle.frame_container.container_start_x + radius + space,
            frame_with_circle.frame_container.container_end_y - (radius + space),
            radius,
            stroke=1,
            fill=1,
        )

        # Add number in circle
        canvas.setFillColor(color_font)
        canvas.setFont("Helvetica", 3)
        canvas.drawCentredString(
            frame_with_circle.frame_container.container_start_x + radius + space,
            frame_with_circle.frame_container.container_end_y - 1.0 * radius - 2.5,
            f"{num}",
        )


class LineFrame:
    def __init__(self, canvas, start_x, end_x, start_y, end_y, stroke_color, stroke_width, fill=0, **kwargs) -> None:
        self.start_x = start_x
        self.end_x = end_x
        self.start_y = start_y
        self.end_y = end_y

        self.frame = Frame(
            start_x,
            start_y,
            abs(end_x - start_x),
            abs(end_y - start_y),
            **kwargs,
        )

        if (fill > 0) or (stroke_width > 0):
            draw_rectangle(
                canvas,
                start_x,
                end_x,
                start_y,
                end_y,
                stroke_color,
                stroke_width,
                fill,
            )


def create_letter(canvas: canvas.Canvas, frame_letter: FrameComposite, **kwargs) -> FrameComposite:
    canvas.setDash(1, 1)

    letter_box_height = frame_letter.frame_container.container_end_y - frame_letter.frame_container.container_start_y
    list_positions = [
        ((0, 50), (0, 100)),
        ((50, 100), (0, 100)),
    ]
    frame_cim_radio, frame_cuv_radio = create_matrix(canvas, frame_letter, list_positions, {**solid_green_line_params, **no_padding_frame_params})

    canvas.setDash(1, 0)

    radio_params = {
        "name": "letter",
        "size": 15,
        "shape": "square",
        "buttonStyle": "check",
        "borderWidth": 0,
        "fillColor": colors.white,
        "borderColor": colors.black,
    }

    radio_cim = canvas.acroForm.radio(
        value="cim",
        x=frame_cim_radio.frame_container.container_end_x - radio_params["size"] - 5,
        y=frame_cim_radio.frame_container.container_center_y - radio_params["size"] / 2,
        **radio_params,
    )

    radio_cuv = canvas.acroForm.radio(
        value="cuv",
        x=frame_cuv_radio.frame_container.container_end_x - radio_params["size"] - 5,
        y=frame_cuv_radio.frame_container.container_center_y - radio_params["size"] / 2,
        **radio_params,
    )

    frame_letter_text_params = {
        "stroke_color": kwargs["stroke_color"],
        "fill": 0,
        "stroke_width": 0,
    }
    frame_letter_text_params.update(no_padding_frame_params)

    frame_cim_text = frame_cim_radio.add_frame(
        canvas=canvas,
        start_x=12,
        end_x=10 + 90,
        start_y=2,
        end_y=letter_box_height,
        **frame_letter_text_params,
    )

    frame_cuv_text = frame_cuv_radio.add_frame(
        canvas=canvas,
        start_x=12,
        end_x=10 + 90,
        start_y=2,
        end_y=letter_box_height,
        **frame_letter_text_params,
    )

    # Remove all margins
    lettre_style = ParagraphStyle(
        "Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        alignment=0,  # Justified text
        textColor=colors.darkgreen,
        spaceAfter=0,
        spaceBefore=0,
        firstLineIndent=0,
        leftIndent=0,
        rightIndent=0,
    )

    frame_cim_text.frame_container.frame.addFromList(
        [Paragraph(f"<b>{paragraph}</b>", style=lettre_style) for paragraph in ["Lettre de voiture CIM", "Frachtbrief CIM"]],
        canvas,
    )

    frame_cuv_text.frame_container.frame.addFromList(
        [Paragraph(f"<b>{paragraph}</b>", style=lettre_style) for paragraph in ["Lettre wagon CUV", "Wagenbrief CUV"]],
        canvas,
    )
    return frame_letter


def get_division_positions(frame: FrameComposite, num_divisions: int) -> dict:
    left_positions = []
    right_positions = []
    center_positions = []
    frame_width = frame.frame_container.container_end_x - frame.frame_container.container_start_x
    for i in range(num_divisions):
        left_positions.append(frame.frame_container.container_start_x + i * frame_width / num_divisions)
        right_positions.append(frame.frame_container.container_start_x + (i + 1) * frame_width / num_divisions)
        center_positions.append((left_positions[i] + right_positions[i]) / 2)

    return {"left": np.array(left_positions), "right": np.array(right_positions), "center": np.array(center_positions)}


def add_equidistant_lines(frame: FrameComposite, canvas: canvas.Canvas, num_lines: int, line_heights=None, offset: float = 0.0):
    frame_height = frame.frame_container.container_end_y - frame.frame_container.container_start_y
    canvas.setDash(1, 1)
    if line_heights is None:
        # 0.5 * frame_height
        line_heights = np.ones(num_lines) * 0.5

    left_positions = get_division_positions(frame, num_lines)["left"]
    for i in range(num_lines):
        start_y = frame.frame_container.container_start_y + offset * frame_height
        end_y = frame.frame_container.container_start_y + (offset + line_heights[i]) * frame_height

        create_line(
            canvas,
            left_positions[i],
            left_positions[i],
            start_y,
            end_y,
            colors.darkgreen,
            0.5,
        )

        create_line(
            canvas,
            left_positions[i],
            left_positions[i],
            start_y,
            end_y,
            colors.darkgreen,
            0.5,
        )
    canvas.setDash(1, 0)


def create_matrix(canvas: canvas.Canvas, frame: FrameComposite, list_positions: list, params) -> list[FrameComposite]:
    frame_width = frame.frame_container.container_end_x - frame.frame_container.container_start_x
    frame_height = frame.frame_container.container_end_y - frame.frame_container.container_start_y
    list_frames = []
    for (start_x, end_x), (start_y, end_y) in list_positions:
        frame_iter = frame.add_frame(
            canvas=canvas,
            start_x=start_x * frame_width / 100,
            end_x=end_x * frame_width / 100,
            start_y=start_y * frame_height / 100,
            end_y=end_y * frame_height / 100,
            **params,
        )
        list_frames.append(frame_iter)

    return list_frames
