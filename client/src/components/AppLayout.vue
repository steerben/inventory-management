<template>
  <div class="app-layout" :class="{ 'app-layout--collapsed': collapsed }">
    <AppSidebar
      @show-profile-details="$emit('show-profile-details')"
      @show-tasks="$emit('show-tasks')"
    />
    <main class="layout-content">
      <slot />
    </main>
  </div>
</template>

<script>
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../composables/useSidebar'

export default {
  name: 'AppLayout',
  components: { AppSidebar },
  emits: ['show-profile-details', 'show-tasks'],
  setup() {
    const { collapsed } = useSidebar()
    return { collapsed }
  }
}
</script>

<style scoped>
.app-layout {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
  /* grid-template-columns is animatable in modern browsers (Chrome 66+, Safari 17+).
     Falls back to instant change in older browsers — acceptable. */
  transition: grid-template-columns var(--transition-base);
}

.app-layout--collapsed {
  grid-template-columns: var(--sidebar-w-collapsed) 1fr;
}

.layout-content {
  min-width: 0;
  background: var(--bg-subtle);
  overflow-y: auto;
  padding: var(--space-5);
}

/* Narrow viewport forces collapsed width regardless of user preference.
   When the user resizes back to wide, their saved preference reapplies. */
@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: var(--sidebar-w-collapsed) 1fr;
  }
}
</style>
