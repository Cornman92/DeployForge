#!/usr/bin/env node

const blessed = require('blessed');
const contrib = require('blessed-contrib');
const axios = require('axios');

// Create screen
const screen = blessed.screen({
  smartCSR: true,
  title: 'DeployForge - Windows Image Configurator',
  fullUnicode: true,
});

// API client
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 30000,
});

// Create main grid
const grid = new contrib.grid({ rows: 12, cols: 12, screen: screen });

// Header
const header = grid.set(0, 0, 1, 12, blessed.box, {
  content: ' DeployForge v1.0.0-alpha - Windows Image Configurator ',
  style: {
    fg: 'white',
    bg: 'blue',
    bold: true,
  },
});

// Sidebar menu
const menu = grid.set(1, 0, 10, 3, blessed.list, {
  label: ' Menu ',
  keys: true,
  vi: true,
  mouse: true,
  style: {
    selected: {
      bg: 'blue',
      fg: 'white',
      bold: true,
    },
    item: {
      fg: 'white',
    },
    border: {
      fg: 'cyan',
    },
  },
  border: {
    type: 'line',
  },
  items: [
    '📊 Dashboard',
    '💿 Images',
    '📦 Components',
    '📝 Registry',
    '🚀 Deployment',
    '⚙️  Workflows',
    '⚙️  Settings',
    '❌ Exit',
  ],
});

// Content area
const content = grid.set(1, 3, 10, 9, blessed.box, {
  label: ' Dashboard ',
  content: 'Loading...',
  scrollable: true,
  alwaysScroll: true,
  keys: true,
  vi: true,
  mouse: true,
  border: {
    type: 'line',
  },
  style: {
    border: {
      fg: 'cyan',
    },
  },
});

// Status bar
const statusBar = grid.set(11, 0, 1, 12, blessed.box, {
  content: ' F1: Help | F10: Menu | ESC: Back | Q: Quit ',
  style: {
    fg: 'white',
    bg: 'blue',
  },
});

// Screens
const screens = {
  dashboard: () => {
    content.setLabel(' Dashboard ');
    content.setContent(
      '\n  {bold}System Status{/bold}\n\n' +
        '  API Status:        {green-fg}Connected{/green-fg}\n' +
        '  Mounted Images:    0\n' +
        '  Active Workflows:  0\n' +
        '  Recent Operations: 0\n\n' +
        '  {bold}Quick Actions{/bold}\n\n' +
        '  1. Mount Image\n' +
        '  2. Run Workflow\n' +
        '  3. Create USB\n' +
        '  4. Generate Answer File\n'
    );
    screen.render();
  },

  images: () => {
    content.setLabel(' Image Manager ');
    content.setContent(
      '\n  {bold}Mounted Images{/bold}\n\n' +
        '  No images currently mounted.\n\n' +
        '  {bold}Available Operations{/bold}\n\n' +
        '  1. Mount WIM/ISO\n' +
        '  2. Mount VHDX\n' +
        '  3. Mount ESD\n' +
        '  4. Unmount All\n' +
        '  5. View Image Info\n'
    );
    screen.render();
  },

  components: () => {
    content.setLabel(' Components ');
    content.setContent(
      '\n  {bold}Component Management{/bold}\n\n' +
        '  Mount an image to view components.\n\n' +
        '  {bold}Available Actions{/bold}\n\n' +
        '  • List Components\n' +
        '  • Add Component\n' +
        '  • Remove Component\n' +
        '  • View Dependencies\n'
    );
    screen.render();
  },

  registry: () => {
    content.setLabel(' Registry Editor ');
    content.setContent(
      '\n  {bold}Registry Tweaks{/bold}\n\n' +
        '  Mount an image to edit registry.\n\n' +
        '  {bold}Preset Categories{/bold}\n\n' +
        '  • Performance Optimization\n' +
        '  • Privacy Settings\n' +
        '  • UI Customization\n' +
        '  • Security Hardening\n'
    );
    screen.render();
  },

  deployment: () => {
    content.setLabel(' Deployment ');
    content.setContent(
      '\n  {bold}Deployment Tools{/bold}\n\n' +
        '  1. Create Bootable USB\n' +
        '  2. Generate Autounattend.xml\n' +
        '  3. Network Deployment Package\n' +
        '  4. PXE Boot Image\n\n' +
        '  {bold}USB Creation{/bold}\n\n' +
        '  • UEFI + Legacy support\n' +
        '  • Multi-boot configuration\n' +
        '  • Rufus/Ventoy integration\n'
    );
    screen.render();
  },

  workflows: () => {
    content.setLabel(' Workflows ');
    content.setContent(
      '\n  {bold}Available Workflows{/bold}\n\n' +
        '  1. Gaming Optimized Windows 11\n' +
        '  2. Enterprise Security Hardened\n' +
        '  3. Minimal/Tiny11\n' +
        '  4. Developer Optimized\n\n' +
        '  {bold}Workflow Status{/bold}\n\n' +
        '  No workflows currently running.\n'
    );
    screen.render();
  },

  settings: () => {
    content.setLabel(' Settings ');
    content.setContent(
      '\n  {bold}Application Settings{/bold}\n\n' +
        '  API Base URL:      http://localhost:5000\n' +
        '  Working Directory: C:\\DeployForge\\Work\n' +
        '  Mount Directory:   C:\\DeployForge\\Mount\n' +
        '  Auto Cleanup:      Enabled\n' +
        '  Telemetry:         Disabled\n\n' +
        '  {bold}DISM Settings{/bold}\n\n' +
        '  Timeout:           3600 seconds\n' +
        '  Log Level:         Warnings\n'
    );
    screen.render();
  },
};

// Menu selection handler
menu.on('select', (item, index) => {
  switch (index) {
    case 0:
      screens.dashboard();
      break;
    case 1:
      screens.images();
      break;
    case 2:
      screens.components();
      break;
    case 3:
      screens.registry();
      break;
    case 4:
      screens.deployment();
      break;
    case 5:
      screens.workflows();
      break;
    case 6:
      screens.settings();
      break;
    case 7:
      process.exit(0);
      break;
  }
});

// Keyboard shortcuts
screen.key(['escape', 'q', 'C-c'], () => {
  process.exit(0);
});

screen.key(['f1'], () => {
  content.setLabel(' Help ');
  content.setContent(
    '\n  {bold}DeployForge TUI - Keyboard Shortcuts{/bold}\n\n' +
      '  Navigation:\n' +
      '  ↑/↓         - Move up/down in menu\n' +
      '  Enter       - Select menu item\n' +
      '  Tab         - Switch focus\n\n' +
      '  Actions:\n' +
      '  F1          - Show this help\n' +
      '  F10         - Focus menu\n' +
      '  ESC         - Back/Exit\n' +
      '  Q           - Quit application\n' +
      '  Ctrl+C      - Force quit\n\n' +
      '  Press any key to return...\n'
  );
  screen.render();
});

screen.key(['f10'], () => {
  menu.focus();
});

// Initialize
menu.focus();
screens.dashboard();

// Check API connectivity
api
  .get('/health')
  .then(() => {
    statusBar.setContent(' {green-fg}●{/green-fg} API Connected | F1: Help | Q: Quit ');
    screen.render();
  })
  .catch(() => {
    statusBar.setContent(' {red-fg}●{/red-fg} API Disconnected | F1: Help | Q: Quit ');
    screen.render();
  });

// Render screen
screen.render();
