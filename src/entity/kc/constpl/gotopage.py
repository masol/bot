

GOTO_PAGE_TPL = """
<script>
	// @ts-nocheck
	import { goto } from '$app/navigation';
    import { browser } from '$app/environment'
    
	if (browser) {
		goto('/{{subdir}}');
	}
</script>
"""
