from odoo import fields, models, api
from odoo.tools import SQL


class BudgetReport(models.Model):
    _inherit = 'budget.report'


    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        sub_plans = self.env['account.analytic.plan'].search([('parent_id', '!=', False)])

        for plan in sub_plans:
            fname = plan._column_name()

            # 3. Si ese campo existe en este reporte, le cambiamos el nombre visible a 'Areas'
            if fname in res:
                res[fname]['string'] = 'Areas'

        return res