from reportlab.pdfgen import canvas
from reportlab.platypus import Frame

from global_vars import A4_height


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
        self.start_x = start_x
        self.end_x = end_x
        self.start_y = start_y
        self.end_y = end_y
        self.center_x = (start_x + end_x) / 2
        self.center_y = (start_y + end_y) / 2
        self.width = abs(end_x - start_x)
        self.height = abs(end_y - start_y)

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
    def __init__(
        self,
        canvas: canvas.Canvas,
        start_x,
        end_x,
        start_y,
        end_y,
        stroke_color,
        stroke_width,
        fill=0,
        offset_x=0,
        offset_y=0,
        **kwargs,
    ) -> None:
        self.start_x = start_x
        self.end_x = end_x

        self.start_y = start_y
        self.end_y = end_y

        self.offset_x = offset_x
        self.offset_y = offset_y

        self.text_fields = []
        self.canvas = canvas
        self.frame_container = FrameContainer(
            canvas,
            self.start_x + self.offset_x,
            self.end_x + self.offset_x,
            A4_height - (self.end_y + offset_y),
            A4_height - (self.start_y + offset_y),
            stroke_color,
            stroke_width,
            fill,
            **kwargs,
        )

    def add_frame(self, canvas, start_x, end_x, start_y, end_y, stroke_color, stroke_width, fill=0, **kwargs):
        frame = FrameComposite(
            canvas,
            start_x,
            end_x,
            start_y,
            end_y,
            stroke_color,
            stroke_width,
            fill,
            offset_x=self.start_x + self.offset_x,
            offset_y=self.start_y + self.offset_y,
            **kwargs,
        )
        return frame


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


def create_matrix(canvas: canvas.Canvas, frame: FrameComposite, list_positions: list, params) -> list[FrameComposite]:
    frame_width = abs(frame.frame_container.end_x - frame.frame_container.start_x)
    frame_height = abs(frame.frame_container.end_y - frame.frame_container.start_y)
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
