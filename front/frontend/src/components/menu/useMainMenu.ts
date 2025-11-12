import { computed, type MaybeRefOrGetter, ref, toValue, watchEffect } from 'vue'

import type { MenuItem } from '@/components/menu/MainMenuItem.vue'

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

export function useMenu (
  items: MaybeRefOrGetter<MenuItem[]>,
  searchQuery: MaybeRefOrGetter<string | null>
) {
  const openedGroups = ref<string[]>([])
  const isSearching = computed<boolean>(() => !!toValue(searchQuery)?.trim())

  watchEffect(() => {
    if (isSearching.value) {
      const currentItems = toValue(items)
      const currentQuery = toValue(searchQuery)!

      openedGroups.value = findOpenGroupsBySearch(currentItems, currentQuery.toLowerCase().trim())
      return
    }
  })

  const filterItems = (itemsToFilter: MenuItem[], query: string): MenuItem[] => {
    const lowerCaseQuery = query.toLowerCase().trim()
    return itemsToFilter
      .map((item): MenuItem | null => {
        if (item.divider) return null

        const titleMatches = item.title?.toLowerCase().includes(lowerCaseQuery) ?? false
        if (titleMatches) {
          return item
        }
        if (item.children) {
          const filteredChildren = filterItems(item.children, query)
          if (filteredChildren.length > 0) {
            return { ...item, children: filteredChildren }
          }
        }
        return null
      })
      .filter((item): item is MenuItem => item !== null)
  }

  const filteredItems = computed<MenuItem[]>(() => {
    const currentQuery = toValue(searchQuery)
    const currentItems = toValue(items)

    return isSearching.value && currentQuery
      ? filterItems(currentItems, currentQuery)
      : currentItems.filter(item => !item.divider)
  })

  return { filteredItems, openedGroups, isSearching }
}
