{% set meta = {
    'import': {"flowbite-svelte": ["Input","Label","Helper"]},
} %}

{% if current %}
<Label class="space-y-2">
    <span>{{current.label}}</span>
    <Input type="email" placeholder="{{current.label}}" size="sm" />
</Label>
{% endif %}
