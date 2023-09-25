{% set meta = {
    'import': {"flowbite-svelte": ["Card"]},
} %}

<div>
    <Card class="mb-4">
        {% for block in blocks %}
            {{block.code}}
        {% endfor %}
    </Card>
</div>