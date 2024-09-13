# Import color
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate

from utils import (
    A4_height,
    A4_width,
    FrameComposite,
    create_line,
    create_matrix,
    no_padding_frame_params,
    solid_black_line_params,
    solid_green_line_params,
    transparent_frame_params,
)

# Main fram parameters
bottom_margin = 50
top_margin = 50
left_margin = 20
right_margin = 20

table_line_height = 3.5

max_num_wagons_per_page = int(100 // table_line_height) - 1

# Paramenters for the header
# Offset over the line
hosy = 2

# Offset next to the line
hosx = 2

# Description height
hdh = 30

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


styles = getSampleStyleSheet()

default_style = {
    "name": "Custom",
    "parent": styles["Normal"],
    "fontName": "Helvetica",
    "textColor": colors.black,
}

small_style = {
    "fontSize": 9,
}

medium_style = {
    "fontSize": 11,
}

big_style = {
    "fontSize": 16,
    "leading": 18,
}

description_style = {**default_style, **small_style}


value_style = {**default_style, **medium_style}

title_style = {**default_style, **big_style, "alignment": 1}

black_color = (0, 0, 0)

# PDF setup
pdf_file = "simple_form.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=A4)

common_style_params = {
    "fontName": "Helvetica",
    "fontSize": 5,
    "leading": 5,
    "alignment": 0,  # Justified text
    "textColor": colors.black,
    "spaceAfter": 5,
    "spaceBefore": 0,
}


def create_page(c: canvas.Canvas, wagon_values, dict_treated_values, last_page=False, last_idx_last_page: int = 0):
    main_frame = FrameComposite(
        c,
        left_margin,
        A4_width - left_margin,
        bottom_margin,
        A4_height - top_margin,
        black_color,
        1,
    )

    dfs = {}
    frames_header = {
        "Versandbahnhof_1_frame": {
            "frame_parent": main_frame,
            "position": ((0, 35), (0, 6)),
        },
        "Versandbahnhof_2_frame": {
            "frame_parent": main_frame,
            "position": ((0, 35), (6, 12)),
        },
        "Leitungswege_frame": {
            "frame_parent": main_frame,
            "position": ((0, 35), (12, 18)),
        },
        "Ort_frame": {
            "frame_parent": main_frame,
            "position": ((65, 100), (12, 18)),
        },
        "Wagenliste_frame": {
            "frame_parent": main_frame,
            "position": ((35, 65), (0, 18)),
        },
        "Ubernahme_frame": {
            "frame_parent": main_frame,
            "position": ((65, 100), (0, 12)),
        },
        "Absender_frame": {
            "frame_parent": main_frame,
            "position": ((0, 28), (18, 24)),
            "text": "Absender",
        },
        "Empfänger_frame": {
            "frame_parent": main_frame,
            "position": ((28, 56), (18, 24)),
            "text": "Empfänger",
        },
        "Zu_verzollen_in_frame": {
            "frame_parent": main_frame,
            "position": ((56, 75), (18, 24)),
            "text": "Zu verzollen in",
        },
        "Begleiter": {
            "frame_parent": main_frame,
            "position": ((75, 100), (18, 24)),
            "text": "Begleiter (Name, Vorname)",
        },
    }

    for key, value in frames_header.items():
        dfs[key] = create_matrix(c, value["frame_parent"], [value["position"]], {**solid_black_line_params, **no_padding_frame_params})[0]

    frames_header_descripitions = {
        "Versandbahnhof_1_description": {
            "frame_parent": dfs["Versandbahnhof_1_frame"],
            "position": ((hosx, 100), (hosy, hdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Versandbahnhof",
        },
        "Versandbahnhof_2_description": {
            "frame_parent": dfs["Versandbahnhof_2_frame"],
            "position": ((hosx, 100), (hosy, hdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Versandbahnhof",
        },
        "Leitungswege_frame_description": {
            "frame_parent": dfs["Leitungswege_frame"],
            "position": ((hosx, 100), (hosy, hdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Leitungswege",
        },
        "Ort_frame_description": {
            "frame_parent": dfs["Ort_frame"],
            "position": ((hosx, 100), (hosy, hdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Ort",
        },
        "Ubernahme_frame_description": {
            "frame_parent": dfs["Ubernahme_frame"],
            "position": ((0, 100), (hosy, hdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": {**description_style, "alignment": 1},
            "text": "Übernahme Monat - Tag - Stunde",
        },
        "Absender_frame_description": {
            "frame_parent": dfs["Absender_frame"],
            "position": ((mosx, 100), (mosy, mdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Absender",
        },
        "Empfänger_frame_description": {
            "frame_parent": dfs["Empfänger_frame"],
            "position": ((mosx, 100), (mosy, mdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Empfänger",
        },
        "Zu_verzollen_in_frame_description": {
            "frame_parent": dfs["Zu_verzollen_in_frame"],
            "position": ((mosx, 100), (mosy, mdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Zu verzollen in",
        },
        "Begleiter_frame_description": {
            "frame_parent": dfs["Begleiter"],
            "position": ((mosx, 100), (mosy, mdh)),
            "params": {**transparent_frame_params, **no_padding_frame_params},
            "text_style": description_style,
            "text": "Begleiter (Name, Vorname)",
        },
    }
    for key, value in frames_header_descripitions.items():
        dfs[key] = create_matrix(c, value["frame_parent"], [value["position"]], value["params"])[0]
        dfs[key].frame_container.frame.addFromList(
            [
                Paragraph(value["text"], style=ParagraphStyle(**value["text_style"])),
            ],
            c,
        )

    frames_Wagenliste = {
        "Bahnhof_frame": {
            "frame_parent": dfs["Wagenliste_frame"],
            "position": ((0, 50), (35, 65)),
            "text": "Bahnhof",
        },
        "Unternehmen_frame": {
            "frame_parent": dfs["Wagenliste_frame"],
            "position": ((50, 100), (35, 65)),
            "text": "Unternehmen",
        },
        "Versand_Nr_frame": {
            "frame_parent": dfs["Wagenliste_frame"],
            "position": ((0, 50), (65, 95)),
            "text": "Versand Nr.",
        },
        "land_frame": {
            "frame_parent": dfs["Wagenliste_frame"],
            "position": ((50, 100), (65, 95)),
            "text": "Land",
        },
    }

    for key, value in frames_Wagenliste.items():
        dfs[key] = create_matrix(c, value["frame_parent"], [value["position"]], {**transparent_frame_params, **no_padding_frame_params})[0]
        dfs[key].frame_container.frame.addFromList(
            [
                Paragraph(value["text"], style=ParagraphStyle(**{**description_style, "alignment": 1})),
            ],
            c,
        )

    dfs["title_frame"] = create_matrix(c, dfs["Wagenliste_frame"], [((0, 100), (0, 30))], {**transparent_frame_params, **no_padding_frame_params})[0]

    dfs["title_frame"].frame_container.frame.addFromList(
        [
            Paragraph("<b>Wagenliste zum Frachtbrief</b>", style=ParagraphStyle(**title_style)),
        ],
        c,
    )

    values_header = {
        "Versandbahnhof_1_value": {
            "frame_parent": dfs["Versandbahnhof_1_frame"],
            "position": ((hosx, 100), (hdh, 100)),
            "text": ["<br/>" + dict_treated_values["Versandbahnhof"][0]],
            "text_params": {**value_style, "alignment": 0},
        },
        "Versandbahnhof_2_value": {
            "frame_parent": dfs["Versandbahnhof_2_frame"],
            "position": ((hosx, 100), (hdh, 100)),
            "text": ["<br/>" + dict_treated_values["Versandbahnhof"][1]],
            "text_params": {**value_style, "alignment": 0},
        },
        "Leitungswege_value": {
            "frame_parent": dfs["Leitungswege_frame"],
            "position": ((hosx, 100), (hdh, 100)),
            "text": dict_treated_values["Leitungswege"],
            "text_params": {**value_style, "alignment": 0},
        },
        "Ort_value": {
            "frame_parent": dfs["Ort_frame"],
            "position": ((hosx, 100), (hdh, 100)),
            "text": dict_treated_values["Ort"],
            "text_params": {**value_style, "alignment": 0},
        },
        "Ubernahme_value": {
            "frame_parent": dfs["Ubernahme_frame"],
            "position": ((0, 100), (hdh, 100)),
            "text": [f"{dict_treated_values['date'][0]}  {dict_treated_values['date'][1]}  {dict_treated_values['date'][2]}"],
            "text_params": {**value_style, "alignment": 1},
        },
        "Absender_value": {
            "frame_parent": dfs["Absender_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Absender"],
            "text_params": {**description_style, "alignment": 0},
        },
        "Empfänger_value": {
            "frame_parent": dfs["Empfänger_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Empfänger"],
            "text_params": {**description_style, "alignment": 0},
        },
        "Zu_verzollen_in_value": {
            "frame_parent": dfs["Zu_verzollen_in_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Zu_verzollen_in"],
            "text_params": {**description_style, "alignment": 0},
        },
        "Begleiter_value": {
            "frame_parent": dfs["Begleiter"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Begleiter"],
            "text_params": {**description_style, "alignment": 0},
        },
        "Bahnhof_value": {
            "frame_parent": dfs["Bahnhof_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Bahnhof"],
            "text_params": {**description_style, "alignment": 1},
        },
        "Unternehmen_value": {
            "frame_parent": dfs["Unternehmen_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Unternehmen"],
            "text_params": {**description_style, "alignment": 1},
        },
        "Versand_Nr_value": {
            "frame_parent": dfs["Versand_Nr_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Versand_Nr"],
            "text_params": {**description_style, "alignment": 1},
        },
        "Land_value": {
            "frame_parent": dfs["land_frame"],
            "position": ((mosx, 100), (moyd, 100)),
            "text": dict_treated_values["Land"],
            "text_params": {**description_style, "alignment": 1},
        },
    }

    for key, value in values_header.items():
        dfs[key] = create_matrix(c, value["frame_parent"], [value["position"]], {**transparent_frame_params, **no_padding_frame_params})[0]
        dfs[key].frame_container.frame.addFromList(
            [Paragraph(f"{text}", style=ParagraphStyle(**value["text_params"])) for text in value["text"]],
            c,
        )

    table_frame, foot_frame = create_matrix(
        c,
        main_frame,
        [((0, 100), (24, 95)), ((0, 100), (95, 100))],
        {**solid_green_line_params, **no_padding_frame_params},
    )

    dict_col_params = {
        "No.": {"col_name": "No.", "position": ((0, 4), (0, 100)), "offset": 40},
        "Wagen": {"col_name": "Wagen", "position": ((4, 23), (0, 100)), "offset": 40},
        "BezDG": {"col_name": "Bezeichnung des Gutes", "position": ((23, 44), (0, 100)), "offset": 40},
        "NHM": {"col_name": "NHM", "position": ((44, 52), (0, 100)), "offset": 40},
        "PN": {"col_name": "Plomben Nummer", "position": ((52, 62), (0, 100)), "offset": 20},
        "RID": {"col_name": "RID", "position": ((62, 64), (0, 100)), "offset": 5},
        "NettoMasse": {"col_name": "Netto Masse", "position": ((64, 76), (0, 100)), "offset": 40},
        "TaraWagon": {"col_name": "Tara Wagon", "position": ((76, 88), (0, 100)), "offset": 40},
        "BruttoMasse": {"col_name": "Brutto Masse", "position": ((88, 100), (0, 100)), "offset": 40},
    }

    for key, value in dict_col_params.items():
        dfs[key + "_frame"] = create_matrix(c, table_frame, [value["position"]], {**solid_black_line_params, **no_padding_frame_params})[0]

        dfs[key + "_frame_description"] = create_matrix(
            c,
            dfs[key + "_frame"],
            [((0, 100), (0, 8))],
            {**solid_black_line_params, **no_padding_frame_params},
        )[0]

        dfs[key + "_frame_values"] = create_matrix(
            c,
            dfs[key + "_frame"],
            [((0, 100), (8, 100))],
            {**solid_black_line_params, **no_padding_frame_params},
        )[0]

        aux = create_matrix(
            c,
            dfs[key + "_frame_description"],
            [((0, 100), (value["offset"], 100))],
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

    for row_idx, wagon in enumerate(wagon_values):
        start_y = table_line_height * row_idx + 0.5
        end_y = table_line_height * (row_idx + 1) + 0.5

        for col_idx, row_name in enumerate(dict_col_params.keys()):
            row_col_frame = create_matrix(
                c,
                dfs[row_name + "_frame_values"],
                [((0, 100), (start_y, end_y))],
                {**transparent_frame_params, **no_padding_frame_params},
            )[0]

            value = wagon.get(row_name, "") if row_name != "No." else row_idx + 1 + last_idx_last_page

            row_col_frame.frame_container.frame.addFromList(
                [
                    Paragraph(f"{value}", style=ParagraphStyle(**{**description_style, "alignment": 1})),
                ],
                c,
            )

    left_foot, right_foot = create_matrix(
        c,
        foot_frame,
        [((0, 50), (0, 100)), ((50, 100), (0, 100))],
        {**solid_black_line_params, "leftPadding": 5, "rightPadding": 5, "topPadding": 5, "bottomPadding": 5},
    )

    left_foot.frame_container.frame.addFromList(
        [
            Paragraph("Ausstellung durch", style=ParagraphStyle(**{**description_style, "alignment": 0})),
            Paragraph("Rail & Sea, Wallerseestrasse 96, AT-5201 Seekirchen", style=ParagraphStyle(**{**value_style, "alignment": 0})),
        ],
        c,
    )

    date = dict_treated_values["date"]

    right_foot.frame_container.frame.addFromList(
        [
            Paragraph("Ort, Datum und Unterschrift", style=ParagraphStyle(**{**description_style, "alignment": 0})),
            Paragraph(f"Seekirchen am {date[0]}.{date[1]}.{date[2]}", style=ParagraphStyle(**{**value_style, "alignment": 0})),
        ],
        c,
    )

    bottom_frame = FrameComposite(
        c,
        left_margin,
        A4_width - left_margin,
        0,
        bottom_margin - 3,
        (1, 0, 0),
        0,
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

    if last_page:
        c.setDash(1, 1)
        create_line(
            c,
            table_frame.start_x,
            table_frame.end_x,
            row_col_frame.frame_container.container_start_y,  # type: ignore
            row_col_frame.frame_container.container_start_y,  # type: ignore
            black_color,
            2,
        )  # ignore

        start_y += 5  # type: ignore # ignore
        end_y += 5  # type: ignore

        masses = dict_treated_values["Sum_masses"]
        for col_name, col_value in zip(["PN", "NettoMasse", "TaraWagon", "BruttoMasse"], ["Sum:"] + masses, strict=False):
            row_col_frame = create_matrix(
                c,
                dfs[col_name + "_frame_values"],
                [((0, 100), (start_y, end_y))],
                {**transparent_frame_params, **no_padding_frame_params},
            )[0]

            row_col_frame.frame_container.frame.addFromList(
                [
                    Paragraph(f"{col_value}", style=ParagraphStyle(**{**description_style, "alignment": 1})),
                ],
                c,
            )

    c.showPage()


def get_treated_values(info_values: dict) -> dict:
    dict_treated_values = {}

    aux = info_values.get("Versandbahnhof", ["", ""])
    if len(aux) == 1:
        aux.append("")

    dict_treated_values["Versandbahnhof"] = aux

    two_line_values = ["Absender", "Empfänger", "Zu_verzollen_in", "Begleiter"]

    for key in two_line_values:
        value = info_values.get(key, ["", ""])
        if len(value) == 1:
            dict_treated_values[key] = ["<br/>" + value[0]]
        else:
            dict_treated_values[key] = value

    single_line_values = ["Leitungswege", "Ort"]

    for key in single_line_values:
        if (key in info_values) and not isinstance(info_values[key], str):
            raise ValueError(f"{key} must be a string")
        dict_treated_values[key] = ["<br/>" + info_values.get(key, "")]

    dict_treated_values["Sum_masses"] = info_values.get("Sum_masses", ["", "", ""])

    date = info_values.get("date", ["", "", ""])

    for key in ["Land", "Bahnhof", "Unternehmen", "Versand_Nr"]:
        value = info_values.get(key, "")
        if not isinstance(info_values.get(value, ""), str):
            raise ValueError(f"{value} must be a string")
        dict_treated_values[key] = [value]

    dict_treated_values["date"] = date

    if len(date) != 3:
        raise ValueError("Date must have 3 values")

    if len(dict_treated_values["Sum_masses"]) != 3:
        raise ValueError("Sum_masses must have 3 values")

    return dict_treated_values


def create_report(wagon_values: list[dict], info_values: dict, report_name: str = "report.pdf"):
    """Create a report with the given values.

    Args:
        wagon_values (list[dict]): List of wagons with the following keys:
            - Wagen: str
            - BezDG (Bezeichnung des Gutes): str
            - NHM: str
            - PN: str
            - RID: str
            - NettoMasse: str
            - TaraWagon: str
            - BruttoMasse: str

        info_values (dict): Dictionary with the following keys:
            Versandbahnhof: List with two values
            Leitungswege: str
            Land: str
            Bahnhof: str
            Unternehmen: str
            Versand_Nr: str
            date: List with three values. eg. ["09", "03", "08"]
            Ort: str
            Sum_masses: List with three values. eg. ["560 380", "158 430", "718 810"]
            Absender: List with one or two values
            Empfänger: List with one or two values
            Zu_verzollen_in: List with one or two values
            Begleiter: List with one or two values


        report_name (str, optional): Name of the report. Defaults to "report.pdf".

    """
    if len(wagon_values) == 0:
        raise ValueError("Wagon values must have at least one element")
    from math import ceil

    dict_treated_values = get_treated_values(info_values)
    c = canvas.Canvas(report_name, pagesize=A4)
    batch_size = max_num_wagons_per_page
    quant_wagons = len(wagon_values)
    batch_config = []
    quant_pages = ceil(quant_wagons / max_num_wagons_per_page)

    for i in range(quant_pages):
        batch_config.append(
            [
                max_num_wagons_per_page * i,
                max_num_wagons_per_page * (i + 1),
                False,
            ],
        )
    batch_config[-1][-1] = True

    for start, end, last_page in batch_config:
        print(f"Creating page for wagons {start} to {end -1}")
        create_page(c, wagon_values[start:end], dict_treated_values, last_page, last_idx_last_page=start)

    c.save()
