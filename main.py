from create_report import create_report
from test_values import info_values, info_values_2, wagon_values

# This creates a report with with some wagons. The report will have the same header in all pages
create_report("report.pdf", wagon_values, info_values, repeat_header=True)
create_report("report_2.pdf", wagon_values, info_values_2, repeat_header=True)

# Same as before but the header will be only in the first page
create_report("report_no_header.pdf", wagon_values, info_values, repeat_header=False)

# This creates a report totally empty with 100 wagons to be filled by the user
create_report("report_empty.pdf", 100, {}, repeat_header=False)

# This creates a report with only one wagon
create_report("report_one_wagon.pdf", wagon_values[:1], info_values, repeat_header=True)

# This creates a report with many wagons with header in all pages
create_report("report_many_wagons.pdf", wagon_values * 10, info_values, repeat_header=True)


# Next two files will not be created because number of wagons is less than 1
create_report("report_no_wagons.pdf", [], {})
create_report("report_no_wagons_2.pdf", 0, {})
