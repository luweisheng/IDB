# -*- coding: utf-8 -*-
import base64

import xlrd
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IdbImportETData(models.TransientModel):
    _name = 'idb.import.et.data'
    _description = 'ET data import'

    name = fields.Char(string='Name', default='ET data import')
    file = fields.Binary(string='File')
    excel_html = fields.Html(string='Excel content')
    excel_text = fields.Text(string='Text content')

    def import_et_data(self):
        # Read the Excel file
        # file_content = self.file
        # if not file_content:
        #     raise UserError(_("Please upload a file."))
        # file_data = base64.b64decode(file_content)
        # workbook = xlrd.open_workbook(file_contents=file_data)
        # sheet = workbook.sheet_by_index(1)
        # data = []
        # for row_idx in range(1, sheet.nrows):
        #     row = sheet.row(row_idx)
        #     row_data = {
        #         'column1': row[0].value,
        #         'column2': row[1].value,
        #     }
        #     data.append(row_data)
        #
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }
        excel_html = self.excel_html
        excel_text = self.excel_text
        return