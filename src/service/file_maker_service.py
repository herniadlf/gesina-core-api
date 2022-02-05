from datetime import datetime
from string import Template


def make_prj_file(title, start_date: datetime, end_date: datetime):
    data = {
        "PROJECT_TITLE": title,
        "START_DATE": start_date.strftime("%d%b%Y"),
        "START_TIME": start_date.strftime("%H:%M"),
        "END_DATE": end_date.strftime("%d%b%Y"),
        "END_TIME": end_date.strftime("%H:%M")
    }
    with open('src/file_templates/prj_template.txt', 'r') as f:
        src = Template(f.read())
    result = src.substitute(data)

    with open(f'{title}.prj', 'w') as f:
        f.write(result)

    return result
