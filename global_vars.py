from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

list_wagon_necessary_keys = ["Wagen", "BezDG", "NHM", "PN", "RID", "NettoMasse", "TaraWagon", "BruttoMasse"]


styles = getSampleStyleSheet()
dark_green_color = (4 / 255, 145 / 255, 103 / 255)

no_padding_frame_params = {"leftPadding": 0, "topPadding": 0, "rightPadding": 0, "bottomPadding": 0}

solid_green_line_params = {"stroke_color": dark_green_color, "stroke_width": 1, "fill": 0}
transparent_frame_params = {"stroke_color": colors.white, "stroke_width": 0, "fill": 0}
solid_black_line_params = {"stroke_color": (0, 0, 0), "stroke_width": 1, "fill": 0}


frame_style = {**solid_black_line_params, **no_padding_frame_params}

frame_dict_font_description_style = {**transparent_frame_params, **no_padding_frame_params}

frame_value_style = {**transparent_frame_params, **no_padding_frame_params}


A4_width, A4_height = A4
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

min_height_header_1 = 30


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


dict_text_field_table_params = {
    "fillColor": colors.transparent,
    "borderWidth": 0,
    "fontName": "Helvetica",
    "fontSize": 10,
}

dict_text_field_header_value_params = {
    "fillColor": colors.transparent,
    "borderWidth": 0,
    "fontName": "Helvetica",
    "fontSize": 11,
    "fieldFlags": "multiline",
    "borderWidth": 0,
}


styles = getSampleStyleSheet()

dict_default_style = {
    "name": "Custom",
    "parent": styles["Normal"],
    "fontName": "Helvetica",
    "textColor": colors.black,
}

dict_font_small_style = {
    "fontSize": 8,
}

dict_font_medium_style = {
    "fontSize": 11,
}

dict_font_big_style = {
    "fontSize": 14,
    "leading": 14,
}

dict_font_description_style = {**dict_default_style, **dict_font_small_style}

dict_font_header_1_value_style = {**dict_default_style, **dict_font_medium_style}

dict_font_value_style = {**dict_default_style, **dict_font_small_style, "alignment": 0}

dict_font_title_style = {**dict_default_style, **dict_font_big_style, "alignment": 1}

dict_font_wagenliste_description_style = {**dict_default_style, **dict_font_small_style, "alignment": 1}
wagenliste_value_style = {**dict_default_style, **dict_font_small_style, "alignment": 1}

frame_description_height = 1.5 * dict_font_description_style["fontSize"]

list_value_names = [
    "Absender",
    "Empfänger",
    "Zu_verzollen_in",
    "Begleiter",
    "Versandbahnhof_1",
    "Versandbahnhof_2",
    "Leitungswege",
    "Ort",
    "Bahnhof",
    "Unternehmen",
    "Versand_Nr",
    "Land",
    "Ausstellung_durch",
]
