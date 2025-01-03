# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IdbSampleManagement(models.Model):
    _inherit = 'mrp.eco'

    # 样板评分明细
    sample_score_ids = fields.One2many('idb.sample.score.line', 'sample_management_id', string='Boilerplate score detail')


class IdbSampleScoreLine(models.Model):
    _name = 'idb.sample.score.line'
    _description = 'Sample Score Line'

    sample_management_id = fields.Many2one('mrp.eco', string='Sample Management')
    # 评分
    score = fields.Float('mark', default=100)
    # 评级
    grade = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ], string='rate', default='A', required=True)
    # 评语
    comment = fields.Html('comment', default='No opinion')


class IdbSampleScore(models.TransientModel):
    _name = 'idb.sample.score'
    _description = 'Sample Score'

    sample_id = fields.Many2one('mrp.eco', string='Sample')
    # 评分
    score = fields.Float('mark', default=100)
    # 评级
    grade = fields.Selection([
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
    ], string='rate', default='A', required=True)
    # 评语
    comment = fields.Html('comment',default='No opinion')

    def action_submit(self):
        sample_id = self.env.context.get('sample_id')
        if sample_id:
            # 创建评分明细
            self.env['idb.sample.score.line'].create({
                'sample_management_id': sample_id,
                'score': self.score,
                'grade': self.grade,
                'comment': self.comment
            })
        return {'type': 'ir.actions.act_window_close'}