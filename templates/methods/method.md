Date: {{ method.created_at|date:"Y-m-d h:m" }}
Author: {{ method.created_by.get_full_name }}
Email: {{ method.created_by.email }}
Title: {{ method.name }}
Slug: {{ method.get_absolute_slug }}
Tags: {{ method.tags.all|join:"," }}

{{ method.notes|safe }}

{% if method.notes %}
> {{ method.notes|safe }}
{% endif %}

{% if method.materials %}#Requirements
{{ method.materials|safe }}{% endif %}

{% if method.notes or method.materials %}#Method{% endif %}
{% for step in method.steps.all %}
{{ step.content|safe }}
{% if step.image %}
![step.image]({{step.image}})
{% endif %}
{% if step.tip %}
> {{ step.tip|safe }}
{% endif %}
{% endfor %}

