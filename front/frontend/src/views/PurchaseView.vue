<template>
  <div class="max-w-xl mx-auto p-6">
    <h2 class="text-2xl font-semibold mb-4">Kup abonament</h2>
    <p class="mb-6 text-gray-600">Po zakupie otrzymasz kod aktywacyjny, którym będziesz mógł powiązać konto z firmą.</p>

    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Kwota (PLN)</label>
        <input v-model.number="amount" type="number" min="1" class="mt-1 block w-full border rounded p-2" />
      </div>

      <button
        :disabled="loading"
        class="bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 disabled:opacity-50"
        @click="startCheckout"
      >
        {{ loading ? 'Przekierowywanie...' : `Kup za ${displayPrice} zł` }}
      </button>

      <p class="text-sm text-gray-500 mt-3">Po zakończeniu płatności wrócisz na stronę i otrzymasz swój kod.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getStripe } from '@/config/stripe'
import { createCheckoutSession } from '@/api/payments'

const auth = useAuthStore()
const amount = ref<number>(99) // domyślna kwota w zł
const loading = ref(false)

const displayPrice = computed(() => `${amount.value}`)

const startCheckout = async () => {
  loading.value = true
  try {
    // Kwota w groszach (Stripe uses minor units)
    const amountCents = Math.round(amount.value * 100)
    const resp = await createCheckoutSession(amountCents)
    if (resp.sessionId) {
      const stripe = await getStripe()
      if (stripe) {
        await stripe.redirectToCheckout({ sessionId: resp.sessionId })
      } else if (resp.url) {
        window.location.href = resp.url
      } else {
        throw new Error('Stripe not available and no fallback url')
      }
    } else if (resp.url) {
      window.location.href = resp.url
    } else {
      throw new Error(resp.error || 'Nieoczekiwany błąd przy tworzeniu sesji')
    }
  } catch (err: any) {
    console.error('Checkout error', err)
    // pokaż snackbar/e alert w UI
    alert(err?.response?.data?.error || err.message || 'Błąd')
  } finally {
    loading.value = false
  }
}
</script>
