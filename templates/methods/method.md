Date: {{ method.created_at|date:"Y-m-d h:m" }}
Author: {{ method.created_by.get_full_name }}
Email: {{ method.created_by.email }}
Title: {{ method.name }}
Slug: {{ method.get_absolute_slug }}
Tags: {{ method.tags.all|join:"," }}

{{ method.description|safe }}

{% if method.image %}
![{{ method.image }}](/static/images/{{method.image|urlencode}})
{% endif %}

{% if method.notes %}
>{{ method.notes_indent|safe }}
{% endif %}

{% if method.materials %}#Requirements
{{ method.materials|safe }}{% endif %}

{% if method.notes or method.materials %}#Method{% endif %}
{% for step in method.steps.all %}
{{ step.content|safe }}
{% if step.image %}
![{{ step.image }}](/static/images/{{step.image|urlencode}})
{% endif %}
{% if step.tip %}
>{{ step.tip_indent|safe }}
{% endif %}
{% endfor %}

{% if method.references.count > 0 %}
#References
{% for reference in method.references.all %}
{% with reference.publication as publication %}
{{ publication.author }} [{{ publication.title }}]({{ publication.url }}) {% if publication.publisher %}_{{ publication.publisher }}_{% endif %} {% if publication.published %}({{ publication.published.year }}){% endif %}
[{% if publication.doi %}{{ publication.doi }}{% else %}{% if publication.pmid %}pmid:{{ publication.pmid }}{% else %}{{ publication.isbn }}{% endif %}{% endif %}]({{ publication.url }})
{% endwith %}
{% endfor %}
{% endif %}
