import { ref } from 'vue'

const STORAGE_KEY = 'sidebar-collapsed'

// Singleton ref: all consumers of useSidebar() share the same reactive state.
// Initialized from localStorage so the user's collapsed/expanded preference
// survives page reloads — matches the standard SaaS sidebar UX (Linear, Stripe).
const collapsed = ref(localStorage.getItem(STORAGE_KEY) === 'true')

export function useSidebar() {
  const toggle = () => {
    collapsed.value = !collapsed.value
    // Persist via simple string flag — avoids JSON parse overhead for a single boolean.
    localStorage.setItem(STORAGE_KEY, String(collapsed.value))
  }

  return { collapsed, toggle }
}
