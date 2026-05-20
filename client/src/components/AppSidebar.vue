<template>
  <aside class="sidebar" :class="{ 'sidebar--collapsed': collapsed }">
    <!-- Brand block -->
    <div class="sidebar-brand">
      <div class="brand-mark">C</div>
      <div class="brand-text">
        <span class="brand-name">{{ t('nav.companyName') }}</span>
        <span class="brand-sub">{{ t('nav.subtitle') }}</span>
      </div>
    </div>

    <!-- Nav list -->
    <nav class="sidebar-nav">
      <router-link
        v-for="route in navRoutes"
        :key="route.path"
        :to="route.path"
        class="nav-item"
        active-class="nav-item--active"
        :exact="route.path === '/'"
        :title="collapsed ? t(route.meta.labelKey) : null"
      >
        <svg
          class="nav-icon"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          aria-hidden="true"
          v-html="icons[route.meta.icon]"
        ></svg>
        <span class="label">{{ t(route.meta.labelKey) }}</span>
      </router-link>
    </nav>

    <!-- Footer -->
    <div class="sidebar-footer">
      <button
        class="collapse-toggle"
        type="button"
        @click="toggle"
        :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        :aria-expanded="!collapsed"
      >
        <svg
          class="nav-icon chevron"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          aria-hidden="true"
          v-html="icons['chevron-left']"
        ></svg>
        <span class="label">Collapse</span>
      </button>
      <LanguageSwitcher />
      <ProfileMenu
        @show-profile-details="$emit('show-profile-details')"
        @show-tasks="$emit('show-tasks')"
      />
    </div>
  </aside>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'
import { useSidebar } from '../composables/useSidebar'
import { icons } from './icons'
import LanguageSwitcher from './LanguageSwitcher.vue'
import ProfileMenu from './ProfileMenu.vue'

export default {
  name: 'AppSidebar',
  components: { LanguageSwitcher, ProfileMenu },
  emits: ['show-profile-details', 'show-tasks'],
  setup() {
    const router = useRouter()
    const { t } = useI18n()
    const { collapsed, toggle } = useSidebar()

    const navRoutes = computed(() => {
      return router.options.routes
        .filter(r => r.meta?.labelKey)
        .slice()
        .sort((a, b) => (a.meta?.order ?? 99) - (b.meta?.order ?? 99))
    })

    return { t, icons, navRoutes, collapsed, toggle }
  }
}
</script>

<style scoped>
.sidebar {
  width: var(--sidebar-w);
  min-height: 100vh;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  transition: width var(--transition-base);
}

.sidebar--collapsed {
  width: var(--sidebar-w-collapsed);
}

/* Brand block */
.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-4);
  height: var(--header-h);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
}

.brand-mark {
  width: 28px;
  height: 28px;
  background: var(--accent);
  border-radius: var(--radius-md);
  color: var(--accent-on);
  font-size: var(--text-sm);
  font-weight: var(--weight-bold);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-family: var(--font-sans);
}

.brand-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand-name {
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.brand-sub {
  font-size: var(--text-xs);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Nav list */
.sidebar-nav {
  flex: 1;
  padding: var(--space-3) var(--space-2);
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  transition: background var(--transition-fast), color var(--transition-fast);
  border-left: 2px solid transparent;
  position: relative;
}

.nav-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.nav-item--active {
  background: var(--accent-soft);
  color: var(--accent);
  border-left-color: var(--accent);
}

.nav-icon {
  flex-shrink: 0;
  color: currentColor;
}

.label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Footer */
.sidebar-footer {
  flex-shrink: 0;
  border-top: 1px solid var(--border-subtle);
  padding: var(--space-3) var(--space-2);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Collapse toggle — styled to match nav-item visual rhythm. */
.collapse-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: var(--weight-medium);
  font-family: inherit;
  cursor: pointer;
  width: 100%;
  text-align: left;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.collapse-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.collapse-toggle:focus-visible {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

/* Chevron points left (collapse) when expanded; flips 180deg when collapsed
   so it points right (expand). Single SVG, single CSS rule — no separate icons. */
.chevron {
  transition: transform var(--transition-base);
}

.sidebar--collapsed .chevron {
  transform: rotate(180deg);
}

/* Collapsed state: hide all text content, center icons.
   Driven by class (.sidebar--collapsed) so it composes with the @media rule below. */
.sidebar--collapsed .brand-text,
.sidebar--collapsed .label {
  display: none;
}

.sidebar--collapsed .sidebar-brand {
  padding: 0;
  justify-content: center;
}

.sidebar--collapsed .nav-item,
.sidebar--collapsed .collapse-toggle {
  justify-content: center;
  padding: var(--space-2);
  gap: 0;
}

/* Narrow viewport — force icon-only regardless of user preference.
   When user resizes back to wide, their saved preference applies again. */
@media (max-width: 768px) {
  .sidebar {
    width: var(--sidebar-w-collapsed);
  }

  .brand-text,
  .label {
    display: none;
  }

  .sidebar-brand {
    padding: 0;
    justify-content: center;
  }

  .nav-item,
  .collapse-toggle {
    justify-content: center;
    padding: var(--space-2);
    gap: 0;
  }

  .chevron {
    transform: rotate(180deg);
  }
}
</style>
