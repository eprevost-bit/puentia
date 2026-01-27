# models/task_template.py
from odoo import models, fields, api

class ProjectTaskTemplate(models.Model):
    _name = 'project.task.template'
    _description = 'Plantilla de Tarea'
    _rec_name = 'name'

    name = fields.Char(string='Nombre de la Tarea', required=True)
    description = fields.Html(string='Descripción')

    # Jerarquía para Subtareas y Sub-subtareas en la plantilla
    parent_id = fields.Many2one('project.task.template', string='Plantilla Padre', ondelete='cascade')
    child_ids = fields.One2many('project.task.template', 'parent_id', string='Subtareas')

    # Campo auxiliar para saber si es una plantilla raíz (para los filtros)
    is_root = fields.Boolean(compute='_compute_is_root', store=True)

    @api.depends('parent_id')
    def _compute_is_root(self):
        for record in self:
            record.is_root = not record.parent_id

    # --- ESTA ES LA FUNCIÓN QUE FALTABA ---
    def open_record(self):
        """
        Abre el formulario de la plantilla actual (hijo) para que el usuario
        pueda añadirle sus propias subtareas (nietos).
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Editar Subtarea Plantilla',
            'view_mode': 'form',
            'res_model': 'project.task.template',
            'res_id': self.id,
            'target': 'current', # 'current' abre en la misma ventana, 'new' en modal
        }