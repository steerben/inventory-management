<template>
  <div class="alerts">
    <PageHeader :title="t('alerts.title')">
      <FilterBar />
    </PageHeader>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <!-- Summary strip -->
      <div class="summary-strip">
        <div class="summary-card out-of-stock">
          <div class="summary-count">{{ countBySeverity('out_of_stock') }}</div>
          <div class="summary-label">{{ t('alerts.summary.outOfStock') }}</div>
        </div>
        <div class="summary-card critical">
          <div class="summary-count">{{ countBySeverity('critical') }}</div>
          <div class="summary-label">{{ t('alerts.summary.critical') }}</div>
        </div>
        <div class="summary-card low">
          <div class="summary-count">{{ countBySeverity('low') }}</div>
          <div class="summary-label">{{ t('alerts.summary.low') }}</div>
        </div>
      </div>

      <!-- Empty state -->
      <div v-if="alerts.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" width="40" height="40" fill="none" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p>{{ t('alerts.emptyState') }}</p>
      </div>

      <!-- Alerts table -->
      <div v-else class="card">
        <div class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('alerts.table.severity') }}</th>
                <th>{{ t('alerts.table.sku') }}</th>
                <th>{{ t('alerts.table.name') }}</th>
                <th>{{ t('alerts.table.category') }}</th>
                <th>{{ t('alerts.table.warehouse') }}</th>
                <th class="num">{{ t('alerts.table.onHand') }}</th>
                <th class="num">{{ t('alerts.table.reorderPoint') }}</th>
                <th class="num">{{ t('alerts.table.unitCost') }}</th>
                <th>{{ t('alerts.table.action') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in alerts" :key="item.sku">
                <td>
                  <span :class="['badge', `severity-${item.severity}`]">
                    {{ t(`alerts.severityLabel.${item.severity}`) }}
                  </span>
                </td>
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ item.name }}</td>
                <td>{{ item.category }}</td>
                <td>{{ item.warehouse }}</td>
                <td class="num">{{ item.quantity_on_hand }}</td>
                <td class="num">{{ item.reorder_point }}</td>
                <td class="num">{{ formatCurrency(item.unit_cost) }}</td>
                <td>
                  <a href="#" class="reorder-link" @click.prevent>{{ t('alerts.action.reorder') }}</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import PageHeader from '../components/PageHeader.vue'
import FilterBar from '../components/FilterBar.vue'

export default {
  name: 'Alerts',
  components: { PageHeader, FilterBar },
  setup() {
    const { t } = useI18n()
    const { selectedLocation, selectedCategory, getCurrentFilters } = useFilters()

    const loading = ref(true)
    const error = ref(null)
    const alerts = ref([])

    // Count items by severity for the summary strip
    const countBySeverity = (severity) => {
      return alerts.value.filter(item => item.severity === severity).length
    }

    const formatCurrency = (value) => {
      return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })
    }

    const loadAlerts = async () => {
      loading.value = true
      error.value = null
      try {
        const filters = getCurrentFilters()
        // alerts endpoint only supports warehouse and category (no time dimension)
        alerts.value = await api.getInventoryAlerts({
          warehouse: filters.warehouse,
          category: filters.category
        })
      } catch (err) {
        error.value = 'Failed to load alerts: ' + err.message
        console.error(err)
      } finally {
        loading.value = false
      }
    }

    watch([selectedLocation, selectedCategory], () => {
      loadAlerts()
    })

    onMounted(loadAlerts)

    return {
      t,
      loading,
      error,
      alerts,
      countBySeverity,
      formatCurrency
    }
  }
}
</script>

<style scoped>
.summary-strip {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.summary-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.5rem;
  border-left: 4px solid transparent;
}

.summary-card.out-of-stock { border-left-color: #ef4444; }
.summary-card.critical     { border-left-color: #f97316; }
.summary-card.low          { border-left-color: #eab308; }

.summary-count {
  font-size: 2rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
}

.summary-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 0.5rem;
}

.card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

thead th {
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

thead th.num { text-align: right; }

tbody td {
  padding: 0.875rem 1rem;
  color: #0f172a;
  border-bottom: 1px solid #f1f5f9;
  white-space: nowrap;
}

tbody td.num { text-align: right; }

tbody tr:last-child td { border-bottom: none; }

tbody tr:hover { background: #f8fafc; }

/* Severity badges */
.badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.severity-out_of_stock { background: #fee2e2; color: #dc2626; }
.severity-critical     { background: #ffedd5; color: #c2410c; }
.severity-low          { background: #fef9c3; color: #a16207; }
.severity-ok           { background: #dcfce7; color: #15803d; }

.reorder-link {
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  font-size: 0.875rem;
}

.reorder-link:hover { text-decoration: underline; }

/* Empty state */
.empty-state {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 4rem 2rem;
  text-align: center;
  color: #64748b;
}

.empty-icon {
  color: #10b981;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

.empty-state p {
  font-size: 1rem;
  font-weight: 500;
  margin: 0;
}

/* Loading / error */
.loading,
.error {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.error { color: #dc2626; }
</style>
