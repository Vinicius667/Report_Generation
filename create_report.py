# Import color
import copy
import logging
import os

from pdfrw import PdfDict, PdfObject, PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from global_vars import (
    A4_height,
    A4_width,
    bottom_margin,
    dict_font_description_style,
    dict_font_header_1_value_style,
    dict_font_title_style,
    dict_text_field_header_value_params,
    dict_text_field_table_params,
    frame_description_height,
    frame_dict_font_description_style,
    frame_style,
    frame_value_style,
    header_1_col_1_width,
    header_1_col_2_width,
    header_1_title_width,
    hosx,
    hosy,
    left_margin,
    list_value_names,
    list_wagon_necessary_keys,
    moyd,
    no_padding_frame_params,
    right_margin,
    solid_black_line_params,
    top_margin,
    transparent_frame_params,
)
from utils import (
    FrameComposite,
    create_line,
    create_matrix,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def get_treated_values(info_values: dict) -> dict:
    dict_treated_values = {}

    for key in list_value_names:
        if key in info_values:
            if isinstance(info_values[key], str):
                dict_treated_values[key] = info_values[key]
            elif isinstance(info_values[key], list):
                dict_treated_values[key] = "<br/>".join(info_values[key])
            else:
                logging.error(f"{key} must be a string or a list. Ignored")
        else:
            dict_treated_values[key] = ""

    date = info_values.get("date", ["", "", ""])
    sum_masses = info_values.get("Sum_masses", ["", "", ""])

    dict_treated_values["Sum_masses"] = sum_masses

    dict_treated_values["date"] = date
    return dict_treated_values


def create_report(filename: str, wagon_values: list[dict] | int, info_values: dict, repeat_header: bool = True) -> int:
    """Create a report with the given values.

    Args:
        wagon_values (list[dict]): List of wagons with the following keys or a integer. When integer is given, the report table will contain this number of empty rows.
            - Wagen: str
            - BezDG (Bezeichnung des Gutes): str
            - NHM: str
            - PN: str
            - RID: str
            - NettoMasse: str
            - TaraWagon: str
            - BruttoMasse: str

        info_values (dict): Dictionary with the following keys. When a list is given, each element will be separated by a line break.

            - Versandbahnhof_1: str or list of str
            - Versandbahnhof_2: str or list of str
            - Leitungswege: str or list of str
            - Ort: str or list of str
            - Bahnhof: str
            - Unternehmen: str
            - Versand_Nr: str
            - Land: str
            - date: List with three values. eg. ["09", "03", "08"]
            - Sum_masses: List with three values. eg. ["560 380", "158 430", "718 810"]
            - Absender: str or list of str
            - Empfänger: str or list of str
            - Zu_verzollen_in: str or list of str
            - Begleiter: str or list of str


        filename (str, optional): Name of the report.

    """
    if not filename.endswith(".pdf"):
        filename += ".pdf"
        logging.warning(f"Filename must end with .pdf. Changed to {filename}")

    if isinstance(wagon_values, int):
        empty_wagon = {key: "" for key in list_wagon_necessary_keys}

        wagon_values = [empty_wagon] * wagon_values

    dict_treated_values = get_treated_values(info_values)

    return _create_report(filename, wagon_values, dict_treated_values, repeat_header)


def _create_report(filename: str, wagon_values: list[dict], dict_treated_values: dict, repeat_header: bool = True) -> int:
    c = canvas.Canvas("temporary.pdf", pagesize=A4)

    wagon_values = copy.deepcopy(wagon_values)

    if len(wagon_values) == 0:
        logging.error("No wagons to create the report")
        return 0

    last_idx_last_page = 0
    is_last_page = False
    count_item = 0
    while len(wagon_values) > 0:
        dfs: dict[str, FrameComposite] = {}
        dfs["main_frame"] = FrameComposite(
            c,
            left_margin,
            A4_width - right_margin,
            bottom_margin,
            A4_height - top_margin,
            (1, 0, 0),
            1,
        )

        must_add_header = repeat_header or last_idx_last_page == 0

        if must_add_header:
            frame_description_text = "Versandbahnhof"

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
                **frame_dict_font_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**dict_font_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Versandbahnhof_1"]
            text_value_style = dict_font_header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = max(1, (len(p.getActualLineWidths0())))

            frame_value_height = 1.3 * text_value_style["fontSize"] * lines_necessary

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

            c.acroForm.textfield(
                name="Versandbahnhof_1_value",
                value=frame_value_text.replace("<br/>", "\n"),
                x=dfs["Versandbahnhof_1_value"].frame_container.start_x,
                y=dfs["Versandbahnhof_1_value"].frame_container.start_y,
                width=dfs["Versandbahnhof_1_value"].frame_container.width,
                height=dfs["Versandbahnhof_1_value"].frame_container.height,
                **dict_text_field_header_value_params,
            )

            frame_description_text = "Versandbahnhof"

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
                **frame_dict_font_description_style,
            )

            dfs["Versandbahnhof_2_description"].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**dict_font_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Versandbahnhof_2"]
            text_value_style = dict_font_header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = max(1, (len(p.getActualLineWidths0())))

            frame_value_height = 1.3 * text_value_style["fontSize"] * lines_necessary

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

            c.acroForm.textfield(
                name="Versandbahnhof_2_value",
                value=frame_value_text.replace("<br/>", "\n"),
                x=dfs["Versandbahnhof_2_value"].frame_container.start_x,
                y=dfs["Versandbahnhof_2_value"].frame_container.start_y,
                width=dfs["Versandbahnhof_2_value"].frame_container.width,
                height=dfs["Versandbahnhof_2_value"].frame_container.height,
                **dict_text_field_header_value_params,
            )

            frame_description_text = "Leitungswege"

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
                **frame_dict_font_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**dict_font_description_style)),
                c,
            )

            min_height = 30

            frame_value_text = dict_treated_values["Leitungswege"]
            text_value_style = dict_font_header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = max(1, 1, len(p.getActualLineWidths0()))

            frame_value_height = 1.3 * text_value_style["fontSize"] * lines_necessary

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

            c.acroForm.textfield(
                name="Leitungswege_value",
                value=frame_value_text.replace("<br/>", "\n"),
                x=dfs["Leitungswege_value"].frame_container.start_x,
                y=dfs["Leitungswege_value"].frame_container.start_y,
                width=dfs["Leitungswege_value"].frame_container.width,
                height=dfs["Leitungswege_value"].frame_container.height,
                **dict_text_field_header_value_params,
            )

            frame_description_text = "Ort"

            frame_value_text = dict_treated_values["Ort"]
            text_value_style = dict_font_header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = max(1, (len(p.getActualLineWidths0())))

            frame_value_height = 1.3 * text_value_style["fontSize"] * lines_necessary

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
            text_value_style = dict_font_header_1_value_style
            p = Paragraph(frame_value_text, style=ParagraphStyle(**text_value_style))
            p.wrap(header_1_col_1_width, 1e6)
            lines_necessary = max(1, (len(p.getActualLineWidths0())))

            frame_value_height = 1.3 * text_value_style["fontSize"] * lines_necessary

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

            c.acroForm.textfield(
                name="Ort_value",
                value=frame_value_text.replace("<br/>", "\n"),
                x=dfs["Ort_value"].frame_container.start_x,
                y=dfs["Ort_value"].frame_container.start_y,
                width=dfs["Ort_value"].frame_container.width,
                height=dfs["Ort_value"].frame_container.height,
                **dict_text_field_header_value_params,
            )

            frame_description_text = "Ort"

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
                **frame_dict_font_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**dict_font_description_style)),
                c,
            )

            frame_name = "Übernahme_frame"

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
                **frame_dict_font_description_style,
            )

            dfs[frame_description_name].frame_container.frame.add(
                Paragraph(frame_description_text, style=ParagraphStyle(**{**dict_font_description_style, "alignment": 1})),
                c,
            )

            date = dict_treated_values["date"]
            frame_value_text = f"{date[0]}  {date[1]}  {date[2]}".strip()

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

            c.acroForm.textfield(
                name="to_be_centered_Ubernahme_value",
                value=frame_value_text.replace("<br/>", "\n"),
                x=dfs["Ubernahme_value"].frame_container.start_x,
                y=dfs["Ubernahme_value"].frame_container.start_y,
                width=dfs["Ubernahme_value"].frame_container.width,
                height=dfs["Ubernahme_value"].frame_container.height,
                **dict_text_field_header_value_params,
            )

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
                    "text_style": {**dict_font_title_style},
                },
                "Bahnhof_frame": {
                    "position": ((0, 50), (35, 65)),
                    "text": "Bahnhof",
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "Unternehmen_frame": {
                    "position": ((50, 100), (35, 65)),
                    "text": "Unternehmen",
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "Versand_Nr_frame": {
                    "position": ((0, 50), (65, 95)),
                    "text": "Versand Nr.",
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "land_frame": {
                    "position": ((50, 100), (65, 95)),
                    "text": "Land",
                    "text_style": {**dict_font_description_style, "alignment": 1},
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
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "Unternehmen_value": {
                    "frame_parent": "Unternehmen_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Unternehmen"],
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "Versand_Nr_value": {
                    "frame_parent": "Versand_Nr_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Versand_Nr"],
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
                "Land_value": {
                    "frame_parent": "land_frame",
                    "position": ((0, 100), (moyd, 100)),
                    "text": dict_treated_values["Land"],
                    "text_style": {**dict_font_description_style, "alignment": 1},
                },
            }

            for key, value in values_header.items():
                dfs[key] = create_matrix(
                    c,
                    dfs[value["frame_parent"]],
                    [value["position"]],
                    {**transparent_frame_params, **no_padding_frame_params},
                )[0]

                c.acroForm.textfield(
                    name=f"to_be_centered_{key}",
                    value=value["text"].replace("<br/>", "\n"),
                    x=dfs[key].frame_container.start_x,
                    y=dfs[key].frame_container.start_y,
                    width=dfs[key].frame_container.width,
                    height=dfs[key].frame_container.height,
                    **dict_text_field_header_value_params,
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

        aux_top, aux_bottom = create_matrix(
            c,
            left_foot,
            [((1.5, 100), (10, 45)), ((1, 100), (50, 100))],
            {**transparent_frame_params, **no_padding_frame_params},
        )

        aux_top.frame_container.frame.addFromList(
            [
                Paragraph(" Ausstellung durch", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 0})),
            ],
            c,
        )

        c.acroForm.textfield(
            name="Ausstellung_durch",
            value=dict_treated_values["Ausstellung_durch"],
            x=aux_bottom.frame_container.start_x,
            y=aux_bottom.frame_container.start_y,
            width=aux_bottom.frame_container.width,
            height=aux_bottom.frame_container.height,
            **dict_text_field_header_value_params,
        )

        aux_top, aux_bottom = create_matrix(
            c,
            right_foot,
            [((1.5, 100), (10, 45)), ((1, 100), (50, 100))],
            {**transparent_frame_params, **no_padding_frame_params},
        )

        aux_top.frame_container.frame.addFromList(
            [
                Paragraph("Ort, Datum und Unterschrift", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 0})),
            ],
            c,
        )

        date = dict_treated_values["date"]

        c.acroForm.textfield(
            name="Ort_Datum_Unterschrift",
            value=f"Seekirchen am {date[0]} {date[1]} {date[2]}",
            x=aux_bottom.frame_container.start_x,
            y=aux_bottom.frame_container.start_y,
            width=aux_bottom.frame_container.width,
            height=aux_bottom.frame_container.height,
            **dict_text_field_header_value_params,
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
                Paragraph("Nur für den kombinierten Verkehr", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 0})),
            ],
            c,
        )

        right_bottom.frame_container.frame.addFromList(
            [
                Paragraph("CIT-23", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 2})),
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
                        Paragraph(f"{value['col_name']}", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 1})),
                    ],
                    c,
                )
            else:
                aux.frame_container.frame.addFromList(
                    [Paragraph(f"{aux}", style=ParagraphStyle(**{**dict_font_description_style, "alignment": 1})) for aux in value["col_name"]],
                    c,
                )

        table_body_height = dfs["table_body_frame"].frame_container.height
        line_height = 18

        quant_wagons_this_page = int(table_body_height // line_height) - 1

        for row_idx in range(quant_wagons_this_page):
            if len(wagon_values) < 1:
                break
            wagon = wagon_values.pop(0)
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
                    **dict_text_field_table_params,
                )
                count_item += 1

        is_last_page = len(wagon_values) == 0

        last_idx_last_page += quant_wagons_this_page

        if is_last_page:
            masses = dict_treated_values["Sum_masses"]
            start_y += line_height  # type: ignore
            end_y += line_height  # type: ignore

            c.setDash(1, 1)
            create_line(
                c,
                dfs["main_frame"].start_x,
                dfs["main_frame"].end_x,
                aux_frame.frame_container.start_y,  # type: ignore
                aux_frame.frame_container.start_y,  # type: ignore
                (0, 0, 0),
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
                    value=col_value.replace("<br/>", "\n"),
                    x=aux_frame.frame_container.start_x,
                    y=aux_frame.frame_container.start_y,
                    width=aux_frame.frame_container.width,
                    height=aux_frame.frame_container.height,
                    **dict_text_field_table_params,
                )
                count_item += 1

        c.showPage()
    c.save()

    temp_file = "temporary.pdf"
    if not os.path.exists(temp_file):
        logging.error(f"File {temp_file} not found")
        return 0

    pdf = PdfReader(temp_file)

    pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject("true")))  # type: ignore

    for page in pdf.pages:  # type: ignore
        if "/Annots" in page:
            for annot in page["/Annots"]:
                if annot.T.startswith("(to_be_centered"):
                    annot.update(PdfDict(Q=1))

    PdfWriter().write(filename, pdf)

    if os.path.exists("temporary.pdf"):
        os.remove("temporary.pdf")

    logging.info(f"File created: {filename}")
    return 1
