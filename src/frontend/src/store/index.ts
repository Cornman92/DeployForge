import { configureStore } from '@reduxjs/toolkit';
import imagesReducer from './slices/imagesSlice';
import componentsReducer from './slices/componentsSlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    images: imagesReducer,
    components: componentsReducer,
    settings: settingsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
