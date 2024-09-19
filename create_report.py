# Import color
import os

from pdfrw import PdfDict, PdfObject, PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from utils import (
    A4_height,
    A4_width,
    FrameComposite,
    create_line,
    create_matrix,
    no_padding_frame_params,
    solid_black_line_params,
    transparent_frame_params,
)

# Main fram parameters
bottom_margin = 50
top_margin = 50
left_margin = 20
right_margin = 20

main_frame_width = A4_width - left_margin - right_margin
main_frame_height = A4_height - top_margin - bottom_margin

header_1_col_1_width = main_frame_width * 0.35
header_1_title_width = main_frame_width * 0.3
header_1_col_2_width = main_frame_width * 0.35
header_2_absender_width = main_frame_width * 0.25
header_2_empfanger_width = main_frame_width * 0.25
header_2_zu_verzollen_in_width = main_frame_width * 0.25
header_2_begleiter_width = main_frame_width * 0.25


# Paramenters for the header
# Offset over the line
hosy = 4

# Offset next to the line
hosx = 2

# Description height
hdh = 15

# Offset y for the description
hoyd = 30

# Parameters for medium frame (Absender, Empfänger, Zu verzollen in, Begleiter)
# Offset over the line
mosy = 2

# Offset next to the line
mosx = 2

# Description height
mdh = 30

# Offset y for the description
moyd = 30


text_field_params = {
    "fillColor": colors.transparent,
    "borderWidth": 0,
    "fontName": "Helvetica",
    "fontSize": 10,
}

styles = getSampleStyleSheet()

default_style = {
    "name": "Custom",
    "parent": styles["Normal"],
    "fontName": "Helvetica",
    "textColor": colors.black,
}

small_style = {
    "fontSize": 8,
}

medium_style = {
    "fontSize": 11,
}

big_style = {
    "fontSize": 14,
    "leading": 14,
}

description_style = {**default_style, **small_style}

header_1_value_style = {**default_style, **medium_style}

header_2_value_style = {**default_style, **small_style, "alignment": 0}

title_style = {**default_style, **big_style, "alignment": 1}

wagenliste_description_style = {**default_style, **small_style, "alignment": 1}
wagenliste_value_style = {**default_style, **small_style, "alignment": 1}


dict_field_value_style = {
    "Versandbahnhof_1": header_1_value_style,
    "Versandbahnhof_2": header_1_value_style,
    "Leitungswege": header_1_value_style,
    "Ort": header_1_value_style,
    "Ubernahme": header_2_value_style,
    "Absender": header_2_value_style,
    "Empfänger": header_2_value_style,
    "Zu_verzollen_in": header_2_value_style,
    "Begleiter": header_2_value_style,
    "Bahnhof": wagenliste_value_style,
    "Unternehmen": wagenliste_value_style,
    "Versand_Nr": wagenliste_value_style,
    "Land": wagenliste_value_style,
}


dict_param_widths = {
    "Versandbahnhof_1": header_1_col_1_width,
    "Versandbahnhof_2": header_1_col_1_width,
    "Leitungswege": header_1_col_1_width,
    "Ort": header_1_col_2_width,
    "Ubernahme": header_1_col_2_width,
    "Absender": header_2_absender_width,
    "Empfänger": header_2_empfanger_width,
    "Zu_verzollen_in": header_2_zu_verzollen_in_width,
    "Begleiter": header_2_begleiter_width,
}

dict_param_heights = {}

two_line_values = ["Absender", "Empfänger", "Zu_verzollen_in", "Begleiter", "Versandbahnhof_1", "Versandbahnhof_2", "Leitungswege", "Ort"]


single_values = ["Bahnhof", "Unternehmen", "Versand_Nr", "Land"]

common_values = two_line_values + single_values


dict_positions = {
    "Versandbahnhof_1": {
        "parent": "main_frame",
        "position": {
            "start_x": 0,
            "end_x": header_1_col_1_width,
            "start_y": 0,
            "end_y": 50,
        },
    },
}


# Header parameters
header_height = 30
header_width = 100


# This a percentage of the height the table body will take
table_line_height = 3.5

max_num_wagons_per_page = int(100 // table_line_height) - 1


black_color = (0, 0, 0)

# PDF setup
pdf_file = "simple_form.pdf"


def get_treated_values(info_values: dict) -> dict:
    dict_treated_values = {}

    for key in two_line_values + single_values:
        if key in info_values:
            if isinstance(info_values[key], str):
                dict_treated_values[key] = info_values[key]
            elif isinstance(info_values[key], list):
                dict_treated_values[key] = "<br/>".join(info_values[key])
            else:
                raise ValueError(f"{key} must be a string or a list")
        else:
            dict_treated_values[key] = ""

    date = info_values.get("date", ["", "", ""])
    sum_masses = info_values.get("Sum_masses", ["", "", ""])

    dict_treated_values["Sum_masses"] = sum_masses

    dict_treated_values["date"] = date

    return dict_treated_values


def create_report(filename: str, wagon_values: list[dict], dict_treated_values: dict, repeat_header: bool = True):
    c = canvas.Canvas("temporary.pdf", pagesize=A4)

    count_wagons_missing = len(wagon_values)
    last_idx_last_page = 0
    is_last_page = False
    count_item = 0
    while count_wagons_missing > 0:
        dfs: dict[str, FrameComposite] = {}
        dfs["main_frame"] = FrameComposite(
            c,
            left_margin,
            A4_width - left_margin,
            bottom_margin,
            A4_height - top_margin,
            (1, 0, 0),
            1,
        )

        must_add_header = repeat_header or last_idx_last_page == 0
        frame_style = {**solid_black_line_params, **no_padding_frame_params}
        frame_description_style = {**transparent_frame_params, **no_padding_frame_params}
        frame_value_style = {**transparent_frame_params, **no_padding_frame_params}
        if must_add_header:
            text_description_style = description_style

            frame_description_text = "Versandbahnhof"
            frame_description_height = 1.5 * text_description_style["fontSize"]
            frame_description_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": hosy,
                "end_y": frame_description_height + hosy,
            }

            parent_frame = "main_frame"

            frame_description_name = "Versandbahnhof_1_description"

            dfs[frame_description_name] = dfs["main_frame"].add_frame(
                c,
                **frame_description_position,
                **frame_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**text_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Versandbahnhof_1"]
            text_value_style = header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = len(p.getActualLineWidths0())

            frame_value_height = 1.1 * text_value_style["fontSize"] * lines_necessary

            frame_height = max(min_height, frame_value_height) + frame_description_height + hosy

            start_y = 0
            end_y = frame_height

            frame_position = {
                "start_x": 0,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Versandbahnhof_1_frame"] = dfs["main_frame"].add_frame(
                c,
                **frame_position,
                **frame_style,
            )

            end_y = dfs["Versandbahnhof_1_frame"].end_y - hosy

            start_y = end_y - frame_value_height

            frame_value_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Versandbahnhof_1_value"] = dfs["main_frame"].add_frame(
                c,
                **frame_value_position,
                **frame_value_style,
            )

            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))

            dfs["Versandbahnhof_1_value"].frame_container.frame.add(p, c)

            frame_description_text = "Versandbahnhof"
            frame_description_height = 1.5 * text_description_style["fontSize"]

            start_y = hosy + dfs["Versandbahnhof_1_frame"].end_y
            end_y = start_y + frame_description_height

            frame_description_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Versandbahnhof_2_description"] = dfs["main_frame"].add_frame(
                c,
                **frame_description_position,
                **frame_description_style,
            )

            dfs["Versandbahnhof_2_description"].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**text_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Versandbahnhof_2"]
            text_value_style = header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = len(p.getActualLineWidths0())

            frame_value_height = 1.1 * text_value_style["fontSize"] * lines_necessary

            frame_height = max(min_height, frame_value_height) + frame_description_height + hosy

            start_y = dfs["Versandbahnhof_1_frame"].end_y
            end_y = start_y + frame_height

            frame_position = {
                "start_x": 0,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Versandbahnhof_2_frame"] = dfs[parent_frame].add_frame(
                c,
                **frame_position,
                **frame_style,
            )

            end_y = dfs["Versandbahnhof_2_frame"].end_y - hosy
            start_y = end_y - frame_value_height

            frame_value_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Versandbahnhof_2_value"] = dfs[parent_frame].add_frame(
                c,
                **frame_value_position,
                **frame_value_style,
            )

            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))

            dfs["Versandbahnhof_2_value"].frame_container.frame.add(p, c)

            frame_description_text = "Leitungswege"
            frame_description_height = 1.5 * text_description_style["fontSize"]

            start_y = hosy + dfs["Versandbahnhof_2_frame"].end_y
            end_y = start_y + frame_description_height

            frame_description_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            frame_description_name = "Leitungswege_frame_description"

            dfs[frame_description_name] = dfs["main_frame"].add_frame(
                c,
                **frame_description_position,
                **frame_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**text_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Leitungswege"]
            text_value_style = header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = len(p.getActualLineWidths0())

            frame_value_height = 1.1 * text_value_style["fontSize"] * lines_necessary

            frame_height = max(min_height, frame_value_height) + frame_description_height + hosy

            start_y = dfs["Versandbahnhof_2_frame"].end_y
            end_y = start_y + frame_height

            frame_position = {
                "start_x": 0,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Leitungswege_frame"] = dfs["main_frame"].add_frame(
                c,
                **frame_position,
                **frame_style,
            )

            end_y = dfs["Leitungswege_frame"].end_y - hosy
            start_y = end_y - frame_value_height

            frame_value_position = {
                "start_x": hosx,
                "end_x": header_1_col_1_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Leitungswege_value"] = dfs["main_frame"].add_frame(
                c,
                **frame_value_position,
                **frame_value_style,
            )

            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))

            dfs["Leitungswege_value"].frame_container.frame.add(p, c)

            frame_description_text = "Ort"
            text_description_style = description_style
            frame_style = {**solid_black_line_params, **no_padding_frame_params}
            frame_description_height = 1.5 * text_description_style["fontSize"]

            frame_value_text = dict_treated_values["Ort"]
            text_value_style = header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = len(p.getActualLineWidths0())

            frame_value_height = 1.1 * text_value_style["fontSize"] * lines_necessary

            frame_height = max(min_height, frame_value_height) + frame_description_height + hosy

            end_y = dfs["Leitungswege_frame"].end_y
            start_y = end_y - frame_height

            frame_position = {
                "start_x": header_1_col_1_width + header_1_title_width,
                "end_x": header_1_col_1_width + header_1_title_width + header_1_col_2_width,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Ort_frame"] = dfs["main_frame"].add_frame(
                c,
                **frame_position,
                **frame_style,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Ort"]
            text_value_style = header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = len(p.getActualLineWidths0())

            frame_value_height = 1.1 * text_value_style["fontSize"] * lines_necessary

            end_y = dfs["Ort_frame"].end_y - hosy
            start_y = end_y - frame_value_height

            frame_value_position = {
                "start_x": dfs["Ort_frame"].start_x + hosx,
                "end_x": dfs["Ort_frame"].end_x,
                "start_y": start_y,
                "end_y": end_y,
            }

            frame_value_name = "Ort_value"

            dfs[frame_value_name] = dfs[parent_frame].add_frame(
                c,
                **frame_value_position,
                **frame_value_style,
            )

            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))

            dfs[frame_value_name].frame_container.frame.add(p, c)

            frame_description_text = "Ort"
            text_description_style = description_style
            frame_style = {**solid_black_line_params, **no_padding_frame_params}
            frame_description_height = 1.5 * text_description_style["fontSize"]

            start_y = hosy + dfs["Ort_frame"].start_y
            end_y = start_y + frame_description_height

            frame_description_position = {
                "start_x": dfs["Ort_frame"].start_x + hosx,
                "end_x": dfs["Ort_frame"].end_x,
                "start_y": start_y,
                "end_y": end_y,
            }

            frame_description_name = "Ort_frame_description"

            dfs[frame_description_name] = dfs["main_frame"].add_frame(
                c,
                **frame_description_position,
                **frame_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**text_description_style)),
                c,
            )

            frame_name = "Übernahme_frame"
            frame_style = {**solid_black_line_params, **no_padding_frame_params}

            start_x = dfs["Ort_frame"].start_x
            end_x = dfs["Ort_frame"].end_x
            end_y = dfs["Ort_frame"].start_y
            start_y = 0

            frame_position = {
                "start_x": start_x,
                "end_x": end_x,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs[frame_name] = dfs[parent_frame].add_frame(
                c,
                **frame_position,
                **frame_style,
            )

            frame_description_text = "Übernahme Monat - Tag - Stunde"
            text_description_style = {**description_style, "alignment": 1}
            frame_style = {**solid_black_line_params, **no_padding_frame_params}
            frame_description_height = 1.5 * text_description_style["fontSize"]

            start_y = hosy
            end_y = start_y + frame_description_height
            frame_description_position = {
                "start_x": dfs["Ort_frame"].start_x,
                "end_x": dfs["Ort_frame"].end_x,
                "start_y": start_y,
                "end_y": end_y,
            }

            parent_frame = "main_frame"

            frame_description_name = "Ubernahme_frame_description"

            dfs[frame_description_name] = dfs[parent_frame].add_frame(
                c,
                **frame_description_position,
                **frame_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**text_description_style)),
                c,
            )

            date = dict_treated_values["date"]
            frame_value_text = f"{date[0]}  {date[1]}  {date[2]}"

            start_y = 2 * hosy + dfs["Ubernahme_frame_description"].end_y
            end_y = start_y + frame_description_height

            frame_value_position = {
                "start_x": dfs["Ort_frame"].start_x,
                "end_x": dfs["Ort_frame"].end_x,
                "start_y": start_y,
                "end_y": end_y,
            }

            dfs["Ubernahme_value"] = dfs[parent_frame].add_frame(
                c,
                **frame_value_position,
                **frame_value_style,
            )

            dfs["Ubernahme_value"].frame_container.frame.add(
                Paragraph(frame_value_text, style=ParagraphStyle(**{**text_value_style, "alignment": 1})),
                c,
            )

            frame_style = {**solid_black_line_params, **no_padding_frame_params}
            dfs["Wagenliste_frame"] = dfs["main_frame"].add_frame(
                c,
                dfs["Versandbahnhof_1_frame"].end_x,
                dfs["Ort_frame"].start_x,
                dfs["Versandbahnhof_1_frame"].start_y,
                dfs["Ort_frame"].end_y,
                **frame_style,
            )

            frames_Wagenliste = {
                "title_frameBahnhof_frame": {
                    "position": ((0, 100), (5, 30)),
                    "text": "<b>Wagenliste zum Frachtbrief</b>",
                    "text_style": {**title_style},
                },
                "Bahnhof_frame": {
                    "position": ((0, 50), (35, 65)),
                    "text": "Bahnhof",
                    "text_style": {**description_style, "alignment": 1},
                },
                "Unternehmen_frame": {
                    "position": ((50, 100), (35, 65)),
                    "text": "Unternehmen",
                    "text_style": {**description_style, "alignment": 1},
                },
                "Versand_Nr_frame": {
                    "position": ((0, 50), (65, 95)),
                    "text": "Versand Nr.",
                    "text_style": {**description_style, "alignment": 1},
                },
                "land_frame": {
                    "position": ((50, 100), (65, 95)),
                    "text": "Land",
                    "text_style": {**description_style, "alignment": 1},
                },
            }

            for key, value in frames_Wagenliste.items():
                dfs[key] = create_matrix(
                    c,
                    dfs["Wagenliste_frame"],
                    [value["position"]],
                    {**transparent_frame_params, **no_padding_frame_params},
                )[0]

                dfs[key].frame_container.frame.add(
                    Paragraph(value["text"], style=ParagraphStyle(**value["text_style"])),
                    c,
                )
            values_header = {
                "Bahnhof_value": {
                    "frame_parent": "Bahnhof_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Bahnhof"],
                    "text_style": {**description_style, "alignment": 1},
                },
                "Unternehmen_value": {
                    "frame_parent": "Unternehmen_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Unternehmen"],
                    "text_style": {**description_style, "alignment": 1},
                },
                "Versand_Nr_value": {
                    "frame_parent": "Versand_Nr_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Versand_Nr"],
                    "text_style": {**description_style, "alignment": 1},
                },
                "Land_value": {
                    "frame_parent": "land_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Land"],
                    "text_style": {**description_style, "alignment": 1},
                },
            }

            for key, value in values_header.items():
                dfs[key] = create_matrix(
                    c,
                    dfs[value["frame_parent"]],
                    [value["position"]],
                    {**transparent_frame_params, **no_padding_frame_params},
                )[0]

                dfs[key].frame_container.frame.add(
                    Paragraph(value["text"], style=ParagraphStyle(**value["text_style"])),
                    c,
                )

            offset_y_start_table = dfs["Ort_frame"].end_y
        else:
            offset_y_start_table = 0

        foot_height = 40
        dfs["table_frame"] = dfs["main_frame"].add_frame(
            c,
            0,
            dfs["main_frame"].frame_container.width,
            offset_y_start_table,
            dfs["main_frame"].frame_container.height - foot_height,
            **{**solid_black_line_params, **no_padding_frame_params},
        )

        dfs["foot_frame"] = dfs["main_frame"].add_frame(
            c,
            0,
            dfs["main_frame"].frame_container.width,
            dfs["main_frame"].frame_container.height - foot_height,
            dfs["main_frame"].frame_container.height,
            **{**solid_black_line_params, **no_padding_frame_params},
        )

        left_foot, right_foot = create_matrix(
            c,
            dfs["foot_frame"],
            [((0, 50), (0, 100)), ((50, 100), (0, 100))],
            {**solid_black_line_params, "leftPadding": 5, "rightPadding": 5, "topPadding": 5, "bottomPadding": 5},
        )

        left_foot.frame_container.frame.addFromList(
            [
                Paragraph("Ausstellung durch", style=ParagraphStyle(**{**description_style, "alignment": 0})),
                Paragraph("Rail & Sea, Wallerseestrasse 96, AT-5201 Seekirchen", style=ParagraphStyle(**{**header_1_value_style, "alignment": 0})),
            ],
            c,
        )

        date = dict_treated_values["date"]

        right_foot.frame_container.frame.addFromList(
            [
                Paragraph("Ort, Datum und Unterschrift", style=ParagraphStyle(**{**description_style, "alignment": 0})),
                Paragraph(f"Seekirchen am {date[0]}.{date[1]}.{date[2]}", style=ParagraphStyle(**{**header_1_value_style, "alignment": 0})),
            ],
            c,
        )

        bottom_frame = dfs["main_frame"].add_frame(
            c,
            0,
            dfs["main_frame"].frame_container.width,
            dfs["main_frame"].frame_container.height + 2,
            dfs["main_frame"].frame_container.height + 20,
            **{**transparent_frame_params, **no_padding_frame_params},
        )

        left_bottom, right_bottom = create_matrix(
            c,
            bottom_frame,
            [((0, 50), (0, 100)), ((50, 100), (0, 100))],
            {**transparent_frame_params, **no_padding_frame_params},
        )

        left_bottom.frame_container.frame.addFromList(
            [
                Paragraph("Nur für den kombinierten Verkehr", style=ParagraphStyle(**{**description_style, "alignment": 0})),
            ],
            c,
        )

        right_bottom.frame_container.frame.addFromList(
            [
                Paragraph("CIT-23", style=ParagraphStyle(**{**description_style, "alignment": 2})),
            ],
            c,
        )

        dfs["table_header_frame"] = dfs["table_frame"].add_frame(
            c,
            0,
            dfs["table_frame"].frame_container.width,
            0,
            45,
            **{**solid_black_line_params, **no_padding_frame_params},
        )

        dfs["table_body_frame"] = dfs["table_frame"].add_frame(
            c,
            0,
            dfs["table_frame"].frame_container.width,
            45,
            dfs["table_frame"].frame_container.height,
            **{**solid_black_line_params, **no_padding_frame_params},
        )

        dict_col_params = {
            "No.": {"col_name": "No.", "position": ((0, 4), (35, 70))},
            "Wagen": {"col_name": "Wagen", "position": ((4, 23), (35, 70))},
            "BezDG": {"col_name": "Bezeichnung des Gutes", "position": ((23, 44), (35, 70))},
            "NHM": {"col_name": "NHM", "position": ((44, 52), (35, 70))},
            "PN": {"col_name": "Plomben Nummer", "position": ((52, 62), (25, 80))},
            "RID": {"col_name": "RID", "position": ((62, 64), (10, 100)), "offset": 5},
            "NettoMasse": {"col_name": "Netto Masse", "position": ((64, 76), (35, 70))},
            "TaraWagon": {"col_name": "Tara Wagon", "position": ((76, 88), (35, 70))},
            "BruttoMasse": {"col_name": "Brutto Masse", "position": ((88, 100), (35, 70))},
        }

        for key, value in dict_col_params.items():
            dfs[key + "_frame"] = create_matrix(
                c,
                dfs["table_header_frame"],
                [(value["position"][0], (0, 100))],
                {**solid_black_line_params, **no_padding_frame_params},
            )[0]

            dfs[key + "_frame_description"] = create_matrix(
                c,
                dfs[key + "_frame"],
                [((0, 100), value["position"][1])],
                {**transparent_frame_params, **no_padding_frame_params},
            )[0]

            dfs[key + "_table_values"] = create_matrix(
                c,
                dfs["table_body_frame"],
                [(value["position"][0], (0, 100))],
                {**solid_black_line_params, **no_padding_frame_params},
            )[0]

            aux = create_matrix(
                c,
                dfs[key + "_frame_description"],
                [((0, 100), (0, 100))],
                {**transparent_frame_params, **no_padding_frame_params},
            )[0]
            if key != "RID":
                aux.frame_container.frame.addFromList(
                    [
                        Paragraph(f"{value['col_name']}", style=ParagraphStyle(**{**description_style, "alignment": 1})),
                    ],
                    c,
                )
            else:
                aux.frame_container.frame.addFromList(
                    [Paragraph(f"{aux}", style=ParagraphStyle(**{**description_style, "alignment": 1})) for aux in value["col_name"]],
                    c,
                )

        table_body_height = dfs["table_body_frame"].frame_container.height
        line_height = 18

        quant_wagons_this_page = int(table_body_height // line_height) - 1

        # print(f"quant_wagons_this_page: {quant_wagons_this_page}")
        for row_idx in range(quant_wagons_this_page):
            count_wagons_missing -= 1
            # print(row_idx, row_idx + last_idx_last_page, count_wagons_missing)

            if count_wagons_missing < 0:
                is_last_page = True
                break

            wagon = wagon_values[row_idx + last_idx_last_page]
            start_y = row_idx * line_height + 2
            end_y = start_y + line_height
            for col_name in dict_col_params:
                value = row_idx + 1 + last_idx_last_page if col_name == "No." else wagon[col_name]

                aux_frame = dfs[col_name + "_table_values"].add_frame(
                    c,
                    0,
                    dfs[col_name + "_table_values"].frame_container.width,
                    start_y,
                    end_y,
                    **{**transparent_frame_params, **no_padding_frame_params},
                )

                c.acroForm.textfield(
                    name=f"to_be_centered_{count_item}",
                    value=f"{value}",
                    x=aux_frame.frame_container.start_x,
                    y=aux_frame.frame_container.start_y,
                    width=aux_frame.frame_container.width,
                    height=aux_frame.frame_container.height,
                    **text_field_params,
                )
                count_item += 1
        last_idx_last_page = quant_wagons_this_page
        # print(f"count_wagons_missing: {count_wagons_missing}")
        # print(f"last_idx_last_page: {last_idx_last_page}")

        if is_last_page:
            masses = dict_treated_values["Sum_masses"]
            start_y += line_height  # type: ignore
            end_y += line_height  # type: ignore

            c.setDash(1, 1)
            create_line(
                c,
                dfs["main_frame"].start_x,
                dfs["main_frame"].end_x,
                aux_frame.frame_container.start_y,
                aux_frame.frame_container.start_y,
                black_color,
                1,
            )

            for col_name, col_value in zip(["PN", "NettoMasse", "TaraWagon", "BruttoMasse"], ["Sum:"] + masses, strict=False):
                aux_frame = dfs[col_name + "_table_values"].add_frame(
                    c,
                    0,
                    dfs[col_name + "_table_values"].frame_container.width,
                    start_y,
                    end_y,
                    **{**transparent_frame_params, **no_padding_frame_params},
                )
                c.acroForm.textfield(
                    name=f"to_be_centered_{count_item}",
                    value=f"{col_value}",
                    x=aux_frame.frame_container.start_x,
                    y=aux_frame.frame_container.start_y,
                    width=aux_frame.frame_container.width,
                    height=aux_frame.frame_container.height,
                    **text_field_params,
                )
                count_item += 1

        c.showPage()

    c.save()

    pdf = PdfReader("temporary.pdf")
    pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject("true")))  # type: ignore

    for page in pdf.pages:  # type: ignore
        if "/Annots" in page:
            for annot in page["/Annots"]:
                if annot.T.startswith("(to_be_centered"):
                    annot.update(PdfDict(Q=1))

    PdfWriter().write(filename, pdf)

    if os.path.exists("temporary.pdf"):
        os.remove("temporary.pdf")

    print(f"File created: {filename}")


if __name__ == "__main__":
    from test_values import info_values, wagon_values

    dict_treated_values = get_treated_values(info_values)

    count_item = create_report("report.pdf", wagon_values + wagon_values + wagon_values, dict_treated_values, repeat_header=False)
