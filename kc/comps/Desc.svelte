{% set meta = {
    'import': {"flowbite-svelte": ["P"]},
} %}

{% if current %}
    <P class="mb-3" weight="light" color="text-gray-500 dark:text-gray-400">
        {{current.label}}
    </P>
{% endif %}
