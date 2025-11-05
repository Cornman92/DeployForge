import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface ImageInfo {
  id: string;
  path: string;
  format: 'WIM' | 'ISO' | 'ESD' | 'VHDX' | 'VHD' | 'IMG' | 'PPKG';
  name: string;
  size: number;
  edition?: string;
  build?: string;
  mountPath?: string;
  isMounted: boolean;
  isReadOnly: boolean;
}

interface ImagesState {
  images: ImageInfo[];
  currentImage: ImageInfo | null;
  loading: boolean;
  error: string | null;
}

const initialState: ImagesState = {
  images: [],
  currentImage: null,
  loading: false,
  error: null,
};

const imagesSlice = createSlice({
  name: 'images',
  initialState,
  reducers: {
    setImages: (state, action: PayloadAction<ImageInfo[]>) => {
      state.images = action.payload;
    },
    addImage: (state, action: PayloadAction<ImageInfo>) => {
      state.images.push(action.payload);
    },
    removeImage: (state, action: PayloadAction<string>) => {
      state.images = state.images.filter((img) => img.id !== action.payload);
    },
    setCurrentImage: (state, action: PayloadAction<ImageInfo | null>) => {
      state.currentImage = action.payload;
    },
    updateImage: (state, action: PayloadAction<ImageInfo>) => {
      const index = state.images.findIndex((img) => img.id === action.payload.id);
      if (index !== -1) {
        state.images[index] = action.payload;
      }
      if (state.currentImage?.id === action.payload.id) {
        state.currentImage = action.payload;
      }
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setImages,
  addImage,
  removeImage,
  setCurrentImage,
  updateImage,
  setLoading,
  setError,
} = imagesSlice.actions;

export default imagesSlice.reducer;
