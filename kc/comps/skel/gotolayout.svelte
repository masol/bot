<script>
  import Header from "$lib/components/header.svelte";
  import Footer from "$lib/components/footer.svelte";
</script>

<Header />
<hr />
<section class="bg-white dark:bg-gray-600 min84">
  <slot />
</section>

<Footer />

<style>
  .min84 {
    min-height: 84vh;
  }
</style>
