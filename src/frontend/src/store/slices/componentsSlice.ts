import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface Component {
  name: string;
  displayName: string;
  description: string;
  size: number;
  category: string;
  isInstalled: boolean;
  isRemovable: boolean;
  dependencies: string[];
}

interface ComponentsState {
  components: Component[];
  loading: boolean;
  error: string | null;
  filter: string;
  categoryFilter: string;
}

const initialState: ComponentsState = {
  components: [],
  loading: false,
  error: null,
  filter: '',
  categoryFilter: 'all',
};

const componentsSlice = createSlice({
  name: 'components',
  initialState,
  reducers: {
    setComponents: (state, action: PayloadAction<Component[]>) => {
      state.components = action.payload;
    },
    updateComponent: (state, action: PayloadAction<Component>) => {
      const index = state.components.findIndex((c) => c.name === action.payload.name);
      if (index !== -1) {
        state.components[index] = action.payload;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    setFilter: (state, action: PayloadAction<string>) => {
      state.filter = action.payload;
    },
    setCategoryFilter: (state, action: PayloadAction<string>) => {
      state.categoryFilter = action.payload;
    },
  },
});

export const { setComponents, updateComponent, setLoading, setError, setFilter, setCategoryFilter } =
  componentsSlice.actions;

export default componentsSlice.reducer;
