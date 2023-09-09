{% set meta = {
    'import': {"flowbite-svelte": ["Heading"]},
} %}

{% if current %}
    <Heading tag="h2" class="mb-4">{{current.label}}</Heading>
{% endif %}
