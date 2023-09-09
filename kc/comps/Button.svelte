{% set meta = {
    'import': {"flowbite-svelte": ["Button"]},
} %}

{% if current %}
<p>
    <Button href="{{current.href}}">{{current.label}}</Button>
</p>
{% endif %}