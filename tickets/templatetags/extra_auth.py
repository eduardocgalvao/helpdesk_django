from django import template

register = template.Library()

# Pesquisando por perfil de acesso
@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

# Retorna a cor do badge baseado na prioridade
@register.filter(name='priority_badge_color')
def priority_badge_color(priority_name):
    """
    Retorna a cor Bootstrap baseada no nome da prioridade:
    - Alta: danger (vermelho)
    - Média: warning (amarelo)
    - Baixa: success (verde)
    """
    if not priority_name:
        return 'secondary'
    
    priority_name_lower = str(priority_name).lower().strip()
    
    if 'alta' in priority_name_lower:
        return 'danger'
    elif 'média' in priority_name_lower or 'media' in priority_name_lower:
        return 'warning'
    elif 'baixa' in priority_name_lower:
        return 'success'
    else:
        return 'secondary'