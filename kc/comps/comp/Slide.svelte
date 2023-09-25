{% set meta = {
    'import': {"flowbite-svelte": ["Range"]},
} %}

{% if current %}
<p>
    <Label>{{current.label}}</Label>
    <Range min="0" max="100" value="50" />
</p>
{% endif %}