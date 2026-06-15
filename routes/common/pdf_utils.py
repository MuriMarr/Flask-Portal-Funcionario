import os
from flask_weasyprint import HTML
from weasyprint import HTML
from flask import render_template

## FUNÇÃO GLOBAL PDF ##
def gerar_pdf(template_name, **kwargs):
    html = render_template(template_name, **kwargs)
    pdf = HTML(string=html).write_pdf()
    return pdf