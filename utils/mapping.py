from data.resume_templates.template_1 import assemble as template_1_assemble,format as format_1,format_rules as format_rule_for_template_1
from data.resume_templates.template_2 import assemble as template_2_assemble,format as format_2,format_rules as format_rule_for_template_2
from data.resume_templates.template_3 import assemble as template_3_assemble,format as format_3,format_rules as format_rule_for_template_3
from data.resume_templates.template_4 import assemble as template_4_assemble,format as format_4,format_rules as format_rule_for_template_4
from data.resume_templates.template_5 import assemble as template_5_assemble,format as format_5,format_rules as format_rule_for_template_5
from data.resume_templates.template_6 import assemble as template_6_assemble,format as format_6,format_rules as format_rule_for_template_6
from importlib import import_module
template_map = {}
assemble_map = {}
format_rules_map = {}
n = 6
for i in range(1,n+1):
    module = import_module(f"data.resume_templates.template_{i}")
    template_map[i] = module.format
    assemble_map[i] = module.assemble
    format_rules_map[i] = module.format_rules
