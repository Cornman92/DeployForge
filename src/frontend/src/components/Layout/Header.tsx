import { Minimize2, Maximize2, X } from 'lucide-react';

export function Header() {
  const handleMinimize = () => {
    if (window.electron) {
      window.electron.minimizeWindow();
    }
  };

  const handleMaximize = () => {
    if (window.electron) {
      window.electron.maximizeWindow();
    }
  };

  const handleClose = () => {
    if (window.electron) {
      window.electron.closeWindow();
    }
  };

  return (
    <header className="titlebar h-12 bg-card border-b border-border flex items-center justify-between px-4">
      <div className="flex items-center gap-4">
        <span className="text-sm font-medium">Windows Image Configurator</span>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={handleMinimize}
          className="p-2 hover:bg-accent rounded transition-colors"
          title="Minimize"
        >
          <Minimize2 className="w-4 h-4" />
        </button>
        <button
          onClick={handleMaximize}
          className="p-2 hover:bg-accent rounded transition-colors"
          title="Maximize"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          onClick={handleClose}
          className="p-2 hover:bg-destructive hover:text-destructive-foreground rounded transition-colors"
          title="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
