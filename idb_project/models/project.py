# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _, _lt
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # 自动获取编号idb.project
    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('idb.project'))
    # 客户
    client_id = fields.Many2one('res.partner', string='Customer', domain=[('customer_rank', '>', 0)], required=True)
    # 客户文件
    client_attachment_ids = fields.Many2many('ir.attachment', 'project_client_attachment_ids', string='Customer file')
    # 包包分类
    category_id = fields.Many2one('product.category', string='Bag Category', domain="[('parent_id', '=', '成品')]", required=True)
    # 客户要求
    client_requirement = fields.Html(string='Customer requirement')

    cg_user_id = fields.Many2one('res.users', string='CG Leader', default=lambda self: self.env.company.cg_user_id.id)

    def action_view_tasks(self):
        res = super(ProjectProject, self).action_view_tasks()
        # 创建项目确认任务，任务接受人成龙
        task_id = self.env['project.task'].create({
            'name': _('客户样板可行性分析'),
            'project_id': self.id,
            'user_ids': self.cg_user_id.ids
        })
        return res