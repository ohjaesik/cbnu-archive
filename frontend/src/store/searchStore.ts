import { create } from 'zustand'
import type { SortOption } from '@/types/project'

interface SearchFilters {
  years: number[]
  semester: 1 | 2 | null
  subjects: string[]
  techStacks: string[]
  domains: string[]
  isTeam: boolean | null
}

interface SearchState {
  keyword: string
  searchType: 'keyword' | 'natural'
  filters: SearchFilters
  sort: SortOption
  page: number
  setKeyword: (keyword: string) => void
  setSearchType: (type: 'keyword' | 'natural') => void
  setFilter: <K extends keyof SearchFilters>(key: K, value: SearchFilters[K]) => void
  setSort: (sort: SortOption) => void
  setPage: (page: number) => void
  resetFilters: () => void
}

const DEFAULT_FILTERS: SearchFilters = {
  years: [],
  semester: null,
  subjects: [],
  techStacks: [],
  domains: [],
  isTeam: null,
}

export const useSearchStore = create<SearchState>((set) => ({
  keyword: '',
  searchType: 'keyword',
  filters: DEFAULT_FILTERS,
  sort: 'latest',
  page: 1,
  setKeyword: (keyword) => set({ keyword, page: 1 }),
  setSearchType: (searchType) => set({ searchType }),
  setFilter: (key, value) =>
    set((state) => ({ filters: { ...state.filters, [key]: value }, page: 1 })),
  setSort: (sort) => set({ sort, page: 1 }),
  setPage: (page) => set({ page }),
  resetFilters: () => set({ filters: DEFAULT_FILTERS, keyword: '', page: 1 }),
}))
