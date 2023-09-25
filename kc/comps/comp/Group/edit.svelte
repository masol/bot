<form>
  <div class="grid gap-6 mb-6 md:grid-cols-2" >
    {% for block in blocks %}
        {{block.code}}
    {% endfor %}
  </div>
</form>
