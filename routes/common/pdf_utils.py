import os
import pdfkit
from flask import render_template

## FUNÇÃO GLOBAL PDF ##
def gerar_pdf(template_name, **kwargs):
    rendered = render_template(template_name, **kwargs)

    wkhtml_path = r"C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe"
    if not os.path.exists(wkhtml_path):
        wkhtml_path = r"C:/Arquivos de Programas/wkhtmltopdf/bin/wkhtmltopdf.exe"

    config = pdfkit.configuration(wkhtmltopdf=wkhtml_path)
    pdf = pdfkit.from_string(rendered, False, configuration=config)
    return pdf