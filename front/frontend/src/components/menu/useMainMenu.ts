import { computed, type Ref, ref } from 'vue'

import type { MenuItem } from '@/config/menuItems'
import { useAuthStore } from '@/stores/auth.ts'

export function findOpenGroupsBySearch (items: MenuItem[], query: string): string[] {
  const groupsToOpen = new Set<string>()

  function traverse (itemsLevel: MenuItem[], parents: string[]): boolean {
    return itemsLevel.reduce((someMatch, item) => {
      const isTitleMatch = item.title?.toLowerCase().includes(query) ?? false

      let hasMatchingChild = false

      if (item.children && item.children.length > 0) {
        hasMatchingChild = traverse(item.children, [...parents, item.title ?? ''])
      }
      if (isTitleMatch || hasMatchingChild) {
        for (const p of parents) {
          groupsToOpen.add(p)
        }

        if (item.children && item.children.length > 0 && item.title) {
          groupsToOpen.add(item.title)
        }

        return true
      }

      return someMatch
    }, false)
  }
  traverse(items, [])
  return Array.from(groupsToOpen)
}

export function useMenu(items: Ref<MenuItem[]>, searchQuery: Ref<string | null>) {
  const authStore = useAuthStore()
  const openedGroups = ref<string[]>([])

  const isSearching = computed(() => !!searchQuery.value && searchQuery.value.trim().length > 0)

  const filterByRole = (menuItems: MenuItem[]): MenuItem[] => {
    return menuItems
      .filter(item => {
        if (item.adminOnly && !authStore.isAdmin) {
          return false
        }
        return true
      })
      .map(item => {
        if (item.children && item.children.length > 0) {
          const filteredChildren = filterByRole(item.children)
          if (filteredChildren.length === 0) {
            return null
          }
          return { ...item, children: filteredChildren }
        }
        return item
      })
      .filter((item): item is MenuItem => item !== null)
  }

  const filterBySearch = (menuItems: MenuItem[], query: string): MenuItem[] => {
    const lowerQuery = query.toLowerCase()

    return menuItems
      .map(item => {
        const titleMatches = item.title?.toLowerCase().includes(lowerQuery) ?? false

        if (item.children && item.children.length > 0) {
          const filteredChildren = filterBySearch(item.children, query)

          if (filteredChildren.length > 0) {
            if (item.title && !openedGroups.value.includes(item.title)) {
              openedGroups.value = [...openedGroups.value, item.title]
            }
            return { ...item, children: filteredChildren }
          }

          if (titleMatches) {
            return item
          }

          return null
        }

        return titleMatches ? item : null
      })
      .filter((item): item is MenuItem => item !== null)
  }

  const filteredItems = computed(() => {
    let result = filterByRole(items.value)

    if (isSearching.value && searchQuery.value) {
      result = filterBySearch(result, searchQuery.value.trim())
    }

    return result
  })

  return {
    filteredItems,
    openedGroups,
    isSearching
  }
}
