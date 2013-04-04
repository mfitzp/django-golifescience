Date: {{ method.created_at|date:"Y-m-d h:m" }}
Author: {{ method.created_by.get_full_name }}
Title: {{ method.name }}
Slug: {{ method.slug }}
Tags: {{ method.tags.all|join:"," }}

{% if method.notes %}
# Notes
{{ method.notes }}
{% endif %}

{% if method.materials %}#Requirements
{{ method.materials }}{% endif %}

#Method
{% for step in method.steps.all %}
{{ step.content }}
{% if step.image %}
![step.image]({{step.image}})
{% endif %}
{% if step.tip %}
<aside>{{ step.tip }}</aside>
{% endif %}
{% endfor %}

