// Type definitions for Electron API exposed via preload script

export interface ElectronAPI {
  getAppVersion: () => Promise<string>;
  getAppPath: (name: string) => Promise<string>;
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<void>;
  closeWindow: () => Promise<void>;
  selectFile: (options: any) => Promise<any>;
  selectDirectory: (options: any) => Promise<any>;
  log: (level: string, message: string) => void;
}

export interface ApiConfig {
  baseUrl: string;
}

declare global {
  interface Window {
    electron: ElectronAPI;
    api: ApiConfig;
  }
}

export {};
