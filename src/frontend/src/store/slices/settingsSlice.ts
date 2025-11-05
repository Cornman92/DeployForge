import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  apiBaseUrl: string;
  workingDirectory: string;
  mountDirectory: string;
  enableAutoCleanup: boolean;
  enableTelemetry: boolean;
}

const initialState: SettingsState = {
  theme: 'dark',
  apiBaseUrl: 'http://localhost:5000',
  workingDirectory: 'C:\\DeployForge\\Work',
  mountDirectory: 'C:\\DeployForge\\Mount',
  enableAutoCleanup: true,
  enableTelemetry: false,
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'system'>) => {
      state.theme = action.payload;
    },
    setApiBaseUrl: (state, action: PayloadAction<string>) => {
      state.apiBaseUrl = action.payload;
    },
    setWorkingDirectory: (state, action: PayloadAction<string>) => {
      state.workingDirectory = action.payload;
    },
    setMountDirectory: (state, action: PayloadAction<string>) => {
      state.mountDirectory = action.payload;
    },
    setEnableAutoCleanup: (state, action: PayloadAction<boolean>) => {
      state.enableAutoCleanup = action.payload;
    },
    setEnableTelemetry: (state, action: PayloadAction<boolean>) => {
      state.enableTelemetry = action.payload;
    },
  },
});

export const {
  setTheme,
  setApiBaseUrl,
  setWorkingDirectory,
  setMountDirectory,
  setEnableAutoCleanup,
  setEnableTelemetry,
} = settingsSlice.actions;

export default settingsSlice.reducer;
