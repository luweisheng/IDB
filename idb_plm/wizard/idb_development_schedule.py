# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class IdbDevelopmentSchedule(models.TransientModel):
    _name = 'idb.development.schedule'
    _description = 'Development sample sheet'

    name = fields.Char(string='Name', default="New")
    # 计划开始日期
    plan_start_date = fields.Date(string='Scheduled start date', default=fields.Date.today)
    # 计划完成日期
    plan_end_date = fields.Date(string='Planned completion date')
    # 出格组长
    leader_id = fields.Many2one('res.users', string='Head of the gang')
    # 出格员
    member_id = fields.Many2one('res.users', string='exceptionalist')
    # 备注
    note = fields.Text(string='Mark')

    def action_confirm(self):
        data = {'state': 'ET',
                'plan_start_date': self.plan_start_date,
                'plan_end_date': self.plan_end_date,
                'leader_id': self.leader_id.id,
                'member_id': self.member_id.id,
                'arrange_note': self.note}
        # 修改状态
        self.env['mrp.eco'].browse(self._context.get('id')).write(data)
        return {'type': 'ir.actions.act_window_close'}
