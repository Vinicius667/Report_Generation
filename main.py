from create_report import create_report, max_num_wagons_per_page
from test_values import info_values, wagon_values

# Test single page
create_report(wagon_values, info_values, "single_page.pdf")

# Test multiple pages
wagon_values = wagon_values * max_num_wagons_per_page
create_report(wagon_values, info_values, "multiple_pages.pdf")

# Test multiple pages with the max number of wagons per page
wagon_values = wagon_values * 10
wagon_values = wagon_values[:max_num_wagons_per_page]

create_report(wagon_values, info_values, "multiple_pages_max.pdf")
