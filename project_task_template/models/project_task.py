# models/project_task.py
from odoo import models, fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_template_id = fields.Many2one('project.task.template', string='Plantilla de Tarea',
                                       domain="[('is_root', '=', True)]")

    @api.onchange('task_template_id')
    def _on_template_change(self):
        """ Carga datos básicos al seleccionar la plantilla (Visual) """
        if self.task_template_id:
            self.name = self.task_template_id.name
            self.description = self.task_template_id.description

    @api.model_create_multi
    def create(self, vals_list):
        """ Sobrescribimos create para generar las subtareas después de guardar la tarea principal """
        tasks = super(ProjectTask, self).create(vals_list)

        for task in tasks:
            if task.task_template_id:
                self._generate_subtasks_from_template(task, task.task_template_id)

        return tasks

    def _generate_subtasks_from_template(self, parent_task, template):
        """ Función recursiva para crear subtareas """
        for template_child in template.child_ids:
            # Crear la subtarea
            subtask_vals = {
                'name': template_child.name,
                'description': template_child.description,
                'project_id': parent_task.project_id.id,  # Esto es suficiente
                'parent_id': parent_task.id,              # Enlace padre/hijo
                # 'display_project_id': parent_task.project_id.id,  <-- ESTA LINEA CAUSABA EL ERROR (ELIMINADA)
            }
            new_subtask = self.create(subtask_vals)

            # RECURSIVIDAD: Si la plantilla hijo tiene sus propios hijos
            if template_child.child_ids:
                self._generate_subtasks_from_template(new_subtask, template_child)