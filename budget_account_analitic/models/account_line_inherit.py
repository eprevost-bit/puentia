from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # 1. Definición de los 3 nuevos campos
    # Usamos store=True para que el rendimiento en los informes sea rápido
    x_project_name = fields.Char(string='Proyecto', compute='_compute_analytic_info', store=True)
    x_analytic_account_names = fields.Char(string='Cuenta Analítica', compute='_compute_analytic_info', store=True)
    x_area_name = fields.Char(string='Area', compute='_compute_analytic_info', store=True)

    @api.depends('analytic_distribution')
    def _compute_analytic_info(self):
        # Pre-buscamos el ID del plan "Proyectos" para no buscarlo en cada línea
        # Ajusta el nombre exacto si en tu base de datos es diferente (ej. mayúsculas)
        project_plan = self.env['account.analytic.plan'].search([('name', '=', 'Proyectos')], limit=1)

        for line in self:
            project_val = ""
            area_val = ""
            all_names = []

            if line.analytic_distribution:
                # 1. Recolectar todos los IDs de cuentas analíticas de esa línea
                analytic_ids = []
                for key in line.analytic_distribution.keys():
                    # El key puede ser "5" o "5,8" si hay múltiples cuentas
                    ids_split = str(key).split(',')
                    for id_str in ids_split:
                        clean_id = id_str.strip()
                        if clean_id.isdigit():
                            analytic_ids.append(int(clean_id))

                if analytic_ids:
                    # 2. Buscar las cuentas en la BD (Una sola consulta es más rápida)
                    accounts = self.env['account.analytic.account'].browse(analytic_ids)

                    # 3. Procesar lógica para cada campo
                    for account in accounts:
                        # Para el campo "Cuenta Analítica" (lista de todas)
                        all_names.append(account.name)

                        # Para el campo "Proyecto"
                        if project_plan and account.plan_id == project_plan:
                            project_val = account.name

                        # Para el campo "Area" (Subplan de Distribución Analítica)
                        # Lógica: Si el plan tiene un padre (parent_id), es un subplan (Area)
                        # O buscamos que el nombre del plan raíz contenga "Distribución Analítica"
                        if account.plan_id.parent_id:
                            # Verificamos si es hijo de Distribución Analítica (opcional, pero más seguro)
                            # Si solo tienes subplanes en Distribución, basta con verificar parent_id
                            area_val = account.name

            # Asignamos los valores finales
            line.x_project_name = project_val
            line.x_analytic_account_names = ", ".join(all_names)
            line.x_area_name = area_val