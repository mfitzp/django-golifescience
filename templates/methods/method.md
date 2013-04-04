Date: {{ method.created_at|date:"Y-m-d h:m" }}
Author: {{ method.created_by.get_full_name }}
Email: {{ method.created_by.email }}
Title: {{ method.name }}
Slug: {{ method.slug }}
Tags: {{ method.tags.all|join:"," }}

{% if method.notes %}
{{ method.notes }}
{% endif %}

{% if method.materials %}#Requirements
{{ method.materials }}{% endif %}

{% if method.notes or method.materials %}#Method{% endif %}
{% for step in method.steps.all %}
{{ step.content }}
{% if step.image %}
![step.image]({{step.image}})
{% endif %}
{% if step.tip %}
<aside>{{ step.tip }}</aside>
{% endif %}
{% endfor %}

