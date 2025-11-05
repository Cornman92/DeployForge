import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  HardDrive,
  Package,
  FileCode2,
  Rocket,
  Workflow,
  Settings,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/images', icon: HardDrive, label: 'Images' },
  { to: '/components', icon: Package, label: 'Components' },
  { to: '/registry', icon: FileCode2, label: 'Registry' },
  { to: '/deployment', icon: Rocket, label: 'Deployment' },
  { to: '/workflows', icon: Workflow, label: 'Workflows' },
  { to: '/settings', icon: Settings, label: 'Settings' },
];

export function Sidebar() {
  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold text-primary">DeployForge</h1>
        <p className="text-sm text-muted-foreground">v1.0.0-alpha</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }`
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-xs text-muted-foreground">
          <p>© 2025 DeployForge</p>
          <p>Windows Image Tool</p>
        </div>
      </div>
    </aside>
  );
}
