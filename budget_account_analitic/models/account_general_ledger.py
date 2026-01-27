from odoo import models, api


class AccountGeneralLedgerReportHandler(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _get_report_line_move_line(self, options, aml_values, partner, line_id):
        # 1. Ejecutamos la función original para obtener los datos básicos
        res = super()._get_report_line_move_line(options, aml_values, partner, line_id)

        # 2. Verificamos que 'line_id' exista (que sea una línea real y no un total)
        if line_id:
            # 3. Asignamos MANUALMENTE el valor a la clave que definiste en la pantalla
            # El nombre entre comillas ['...'] debe ser IDENTICO a tu "Etiqueta de expresión"

            # Campo Proyecto
            res['x_project_name'] = line_id.x_project_name or ''

            # Campo Area
            res['x_area_name'] = line_id.x_area_name or ''

            # Campo Cuenta Analítica
            res['x_analytic_account_names'] = line_id.x_analytic_account_names or ''

        return res