# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IdbDevelopType(models.Model):
    _name = 'idb.develop.type'
    _description = 'Development type'

    name = fields.Char(string='Name')
    code = fields.Char(string='code')


class IdbRejectReason(models.TransientModel):
    _name = 'idb.reject.reason'
    _description = 'Cause of rejection'

    name = fields.Char(string='Cause of rejection')

    # sample_management_id = fields.Many2one('idb.sample.management', string='样品管理')

    def submit_reject_reason(self):
        sample_management_id = self.env['idb.sample.management'].browse(self.env.context.get('id'))
        # 返回上级状态
        state = {
            'main_material_purchase': 'draft',
            'development_release_scheduled': 'material_purchase',
            'ET': 'development_release_scheduled',
            'material_purchase': 'ET',
            'plate_making': 'material_purchase',
            'sample_inspection': 'plate_making',
            'DHL': 'sample_inspection',
            'done': 'DHL',
        }.get(sample_management_id.state)
        sample_management_id.write({'state': state})
        sample_management_id.message_post(body=self.name)
        return {'type': 'ir.actions.act_window_close'}


class IdbSampleManagement(models.Model):
    _name = 'idb.sample.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sample management'

    name = fields.Char(string='单号', default="New", copy=False, readonly=True)
    image = fields.Binary("Image")
    # 开发日期
    develop_date = fields.Date(string='Development date', default=fields.Date.today, track_visibility='onchange')
    # 交版日期
    delivery_date = fields.Date(string='Delivery date', track_visibility='onchange')
    # 客户 仅显示客户
    customer_id = fields.Many2one('res.partner',
                                  string='client',
                                  track_visibility='onchange',
                                  domain=[('customer_rank', '>', 0)],
                                  required=True
                                  )
    # 客户号
    customer_number = fields.Char(string='Client number', related='customer_id.barcode')
    # 客户款号
    customer_factory_number = fields.Char(string='Customer account number')
    # 业务员
    salesperson_id = fields.Many2one('res.users', string='business', default=lambda self: self.env.user,
                                     track_visibility='onchange')
    # 工厂款号
    factory_number = fields.Char(string='Style number', track_visibility='onchange')
    # 开发类型
    develop_type_id = fields.Many2one('idb.develop.type', string='Development type', track_visibility='onchange')
    # 系列
    series = fields.Char(string='Product series', track_visibility='onchange')
    # 备注
    note = fields.Char(string='Mark', track_visibility='onchange')
    # 样品管理明细
    sample_management_line_ids = fields.One2many('idb.sample.management.line', 'sample_management_id',
                                                 string='Sample management detail', copy=True)
    # 产品分类
    category_id = fields.Many2one('product.category', string='Product classification',
                                  required=True,
                                  domain=[('parent_id', '=', 'Finished product')])

    # 委外
    is_outsourcing = fields.Boolean(string='outsource')
    # 委外商
    outsourcing_partner_id = fields.Many2one('res.partner', string='Merchant contractor')

    def _get_factory_number(self, category_id):
        # 查询当前月份的最大流水号
        last_sample = self.search([
            ('factory_number', 'like', category_id.barcode + fields.Date.today().strftime('%Y%m') + '%')],
            order='factory_number desc', limit=1)
        if last_sample:
            factory_number = last_sample.factory_number
            # factory_number = category_id.barcode + fields.Date.today().strftime('%Y%m') + str(
            #     int(factory_number[-3:]) + 1).zfill(3)
            factory_number = 'IDB' + fields.Date.today().strftime('%Y%m') + str(
                int(factory_number[-3:]) + 1).zfill(3)
        else:
            factory_number = category_id.barcode + fields.Date.today().strftime('%Y%m') + '001'
        return factory_number

    @api.onchange('category_id')
    def _onchange_category_id(self):
        # 根据类别码自动生成款号=类别码+年月+3位流水号
        if self.category_id:
            factory_number = self._get_factory_number(self.category_id)
            self.factory_number = factory_number

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default['name'] = self.env['ir.sequence'].next_by_code('idb.sample.management')
        default['state'] = 'draft'
        default['factory_number'] = self._get_factory_number(self.category_id)
        return super(IdbSampleManagement, self).copy(default)

    # 配色表
    color_id = fields.Many2one('idb.product.color', string='Product main color')
    # 规格
    specification = fields.Char(string='Product specification')
    # 数量
    quantity = fields.Integer(string='quantity', default=1)
    # 单价
    price = fields.Float(string='price', default=0.0)

    state = fields.Selection([
        ('draft', 'draft'),
        ('main_material_purchase', 'Main materials purchasing'),
        ('development_release_scheduled', 'Development release is scheduled'),
        ('ET', 'ET out of line'),
        ('material_purchase', 'General stores purchasing'),
        ('plate_making', 'plate-making'),
        ('stock_preparation', 'Stock preparation'),
        ('cutting', 'cutting'),
        ('oil_edge', 'Oil edge'),
        ('table', 'table'),
        ('parking_space', 'Parking space'),
        ('sample_inspection', 'Sample inspection'),
        ('DHL', 'Shipping version - DHL'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], string='status', default='draft', track_visibility='onchange')

    # 样品单模板
    order_template_id = fields.Many2one('sample.development.single.template',
                                        string='template',
                                        default=lambda self: self.env.company.order_template_id,
                                        track_visibility='onchange')

    @api.onchange('order_template_id')
    def _onchange_order_template_id(self):
        if self.order_template_id:
            self.sample_management_line_ids = None
            self.sample_management_line_ids = [(0, 0, {
                'accessory_id': line.accessory_id.id,
                'is_required': line.is_required,
            }) for line in self.order_template_id.sample_development_single_template_line_ids]

    def action_confirm(self):
        for line in self.sample_management_line_ids:
            # 根据accessory_id配置的必填项判断是否填写
            if line.is_required and not line.main_product_id:
                raise UserError(_('{}Not filled! Prohibit submission！'.format(line.accessory_id.name)))
        self.write({'state': 'main_material_purchase'})

    def submission_schedule(self):
        purchase_data = {}
        for line in self.sample_management_line_ids:
            # 根据accessory_id配置的必填项判断是否填写
            if line.main_product_id and not line.partner_id:
                raise UserError(_('{}No supplier! Submission prohibited!'.format(line.accessory_id.name)))
            partner_id = line.partner_id.id
            if partner_id:
                order_line = (0, 0, {
                    'product_id': line.main_product_id.id,
                    'name': line.main_product_id.name,
                    'product_qty': line.product_qty,
                    'price_unit': line.price,
                    'sample_management_line_id': line.id,
                })
                if partner_id not in purchase_data:
                    purchase_data[partner_id] = {
                        'sample_management_id': self.id,
                        'idb_purchase_type': 'main',
                        'order_line': [order_line],
                    }
                else:
                    purchase_data[partner_id]['order_line'].append(order_line)
        for key, value in purchase_data.items():
            self.env['purchase.order'].create({'partner_id': key, **value})
        # # 创建询价单
        # self.env['purchase.order'].create({
        #     'sample_management_id': self.id,
        #     'order_line': [(0, 0, {
        #         'product_id': line.main_product_id.id,
        #         'name': line.main_product_id.name,
        #         'product_qty': line.product_qty,
        #         'price_unit': line.price,
        #         'sample_management_line_id': line.id,
        #     }) for line in self.sample_management_line_ids if line.main_product_id and line.partner_id],
        # })
        self.write({'state': 'development_release_scheduled'})

    # 排期提交
    def arrange_exceed_the_norm(self):
        # 打开窗口填写排期内容
        return {
            'name': _('Fill in the schedule content'),
            'type': 'ir.actions.act_window',
            'res_model': 'idb.development.schedule',
            'view_mode': 'form',
            'context': {'id': self.id},
            'target': 'new',
        }

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def sample_inspection(self):
        self.write({'state': 'sample_inspection'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('idb.sample.management') or _("New")
        return super(IdbSampleManagement, self).create(vals_list)

    @api.model
    def default_get(self, field_list):
        res = super(IdbSampleManagement, self).default_get(field_list)
        # 获取默认模板
        template = self.env.company.order_template_id
        data = {}
        if template:
            data['sample_management_line_ids'] = [(0, 0, {
                'accessory_id': line.accessory_id.id,
                'is_required': line.is_required,
            }) for line in template.sample_development_single_template_line_ids]
        if data:
            res.update(data)
        return res

    # 要求内容
    required_content = fields.Html(string='Required content')

    # 计划开始日期
    plan_start_date = fields.Date(string='Scheduled start date')
    # 计划完成日期
    plan_end_date = fields.Date(string='Planned completion date')

    # 计划完成天数
    plan_day = fields.Float('Scheduled completion days', compute="_compute_plan_day")

    @api.depends('plan_start_date', 'plan_end_date')
    def _compute_plan_day(self):
        for line in self:
            plan_day = 0
            if line.plan_start_date and line.plan_end_date:
                plan_day = (line.plan_end_date - line.plan_start_date).days
            line.plan_day = plan_day

    # 出格组长
    leader_id = fields.Many2one('res.users', string='Head of the gang')
    # 出格员
    member_id = fields.Many2one('res.users', string='exceptionalist')
    # 排期备注
    arrange_note = fields.Text(string='Scheduling remarks')

    # 异常问题记录明细表
    abnormal_problem_record_ids = fields.One2many('idb.abnormal.problem.record', 'sample_management_id',
                                                  string='Exception problem log list')

    # 提交做版
    def submission_plate_making(self):

        self.write({'state': 'plate_making'})

    purchase_count = fields.Integer(string='Purchase order quantity', compute='_compute_purchase_count')

    @api.model
    def _compute_purchase_count(self):
        for record in self:
            record.purchase_count = self.env['purchase.order.line'].search_count([('order_id.sample_management_id', '=', record.id)])

    def action_open_purchase_order(self):
        return {
            'name': _('Purchase details'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_mode': 'tree',
            'context': {'tree_view_ref': 'idb_basic_data.idb_purchase_order_line_tree'},  # 指定树视图
            'domain': [('order_id.sample_management_id', '=', self.id)]
        }

    def action_reject(self):
        # 弹窗填写驳回原因
        return {
            'name': _('Reason for rejection'),
            'type': 'ir.actions.act_window',
            'res_model': 'idb.reject.reason',
            'view_mode': 'form',
            'context': {'id': self.id},
            'target': 'new',
        }

    def general_material_preparation(self):
        if self.bom_count <= 0:
            raise UserError(_('Product BOM not created, do not submit next step! Please perform ET data generation BOM operation!'))
            # 检查部位资料是否填写产品
        for bom_line_id in self.bom_id.bom_line_ids:
            if not bom_line_id.product_id:
                raise UserError(_('Position information and products are not filled in, do not submit the next step!'))
        # 检查无部位资料是否填写产品
        for no_bom_line_id in self.bom_id.no_bom_line_ids:
            if not no_bom_line_id.product_id:
                raise UserError(_('No part information and products are not filled in, do not submit the next step!'))
        self.write({'state': 'material_purchase'})

    # def import_et_data(self):
    #     # 导入ET数据
    #     return {
    #         'name': _('导入ET数据'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'idb.import.et.data',
    #         'view_mode': 'form',
    #         'context': {'id': self.id},
    #         'target': 'new',
    #     }

    def sample_score(self):
        return {
            'name': _('Sample score'),
            'type': 'ir.actions.act_window',
            'res_model': 'idb.sample.score',
            'view_mode': 'form',
            'context': {'sample_id': self.id},
            'target': 'new',
        }

    def pass_inspection(self):
        self.write({'state': 'DHL'})

    def shipping_sample(self):
        self.write({'state': 'done'})

    # 客户评语
    customer_comment_ids = fields.One2many('idb.customer.comment', 'sample_management_id', string='Customer comments')

    bom_id = fields.Many2one('mrp.bom', string='Product BOM')


class IdbSampleManagementLine(models.Model):
    _name = 'idb.sample.management.line'
    _description = 'Sample management detail'

    sample_management_id = fields.Many2one('idb.sample.management', string='Sample management')
    sequence = fields.Integer(string='Serial number')
    # 名称
    accessory_id = fields.Many2one('idb.product.accessory.type', string='category')
    is_required = fields.Boolean(string='required')
    # category_id = fields.Many2one('product.category', string='类别')
    # 产品主色
    main_color_id = fields.Many2one('idb.product.color', string='Dominant colour')
    # 主料
    main_product_id = fields.Many2one('product.product', string='Materials', domain=[('material_type', '=', 'material'),
                                                                                ('categ_id.parent_id', '!=', 'Finished product')])
    # 供应商
    partner_id = fields.Many2one('res.partner', string='supplier', domain=[('supplier_rank', '>', 0)],)
    # 价格表
    price_id = fields.Many2one('product.supplierinfo', string='Price list')
    # 价格
    price = fields.Float(string='Price', default=1)
    # 数量
    product_qty = fields.Float(string='quantity', default=1)
    # 单位
    product_uom_id = fields.Many2one('uom.uom', string='unit')

    @api.onchange('main_product_id')
    def _onchange_main_product_id(self):
        if self.main_product_id:
            self.product_uom_id = self.main_product_id.uom_id.id

    # 说明
    note = fields.Html(string='Instructions')
    attachment_ids = fields.Many2many('ir.attachment', string='attachments')

    def create_main_product(self):
        # create_product_template_id = self.env['idb.create.product.template'].create({
        #     'name': self.accessory_id.name
        # })
        return {
            'name': _('Create product'),
            'type': 'ir.actions.act_window',
            'res_model': 'idb.create.product.template',
            'view_mode': 'form',
            'context': {'sample_management_line_id': self.id},
            # 'res_id': create_product_template_id.id,
            'target': 'new',
        }


class IdbAbnormalProblemRecordType(models.Model):
    _name = 'idb.abnormal.problem.record.type'
    _description = 'Exception problem record type'

    name = fields.Char(string='name')
    code = fields.Char(string='code')


class IdbAbnormalProblemRecord(models.Model):
    _name = 'idb.abnormal.problem.record'
    _description = 'Exception problem log'

    sample_management_id = fields.Many2one('idb.sample.management', string='Sample management')
    # 问题描述
    problem_description = fields.Text(string='Problem description')
    # 问题类型
    problem_type_id = fields.Many2one('idb.abnormal.problem.record.type', string='Problem type')
    # 责任人
    responsible_person_id = fields.Many2one('res.users', string='Person in charge')
    # 备注
    note = fields.Text(string='remark')


class IdbCreateProductTemplate(models.TransientModel):
    _inherit = 'idb.create.product.template'

    def create_product(self):
        # name = []
        # for line in self.value_line:
        #     name.append(line.product_attribute_id.name + ':' + line.product_attribute_value_id.name + '')
        # name = ','.join(name)
        name = ''
        for line in self.value_line:
            name += line.product_attribute_value_id.name
        # 创建产品
        product_id = self.env['product.template'].create({
            'name': name,
            'categ_id': self.category_id.id,
            'uom_po_id': self.po_uom_id.id,
            'uom_id': self.uom_id.id,
        })
        sample_management_line_id = self.env['idb.sample.management.line'].browse(
            self.env.context.get('sample_management_line_id'))
        sample_management_line_id.write({'main_product_id': product_id.id})
        return super(IdbCreateProductTemplate, self).create_product()


class IdbCustomerComment(models.Model):
    _name = 'idb.customer.comment'
    _description = 'Customer comments'

    sample_management_id = fields.Many2one('idb.sample.management', string='Sample management')
    # 评语
    comment = fields.Html(string='comment')
    # 评分
    score = fields.Float(string='score', default=100)
    # 评价日期
    comment_date = fields.Date(string='comment date', default=fields.Date.today)
    # 评价人
    comment_person_id = fields.Many2one('res.users', string='comment user', default=lambda self: self.env.user)
