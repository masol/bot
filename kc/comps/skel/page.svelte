<script>
    {% if pageinfo %}
    {{render_importer(pageinfo.importer)}}
    {% endif %}
</script>

{% for block in blocks %}
    {{block.code}}
{% endfor %}