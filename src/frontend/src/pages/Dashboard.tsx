export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to DeployForge - Windows Image Configurator
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Mounted Images</h3>
          <p className="text-3xl font-bold text-primary">0</p>
          <p className="text-sm text-muted-foreground mt-2">No images currently mounted</p>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Active Workflows</h3>
          <p className="text-3xl font-bold text-primary">0</p>
          <p className="text-sm text-muted-foreground mt-2">No workflows running</p>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-2">Recent Operations</h3>
          <p className="text-3xl font-bold text-primary">0</p>
          <p className="text-sm text-muted-foreground mt-2">No recent operations</p>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="p-4 border border-border rounded-lg hover:bg-accent transition-colors text-left">
            <h3 className="font-semibold mb-1">Mount Image</h3>
            <p className="text-sm text-muted-foreground">Load a Windows image file</p>
          </button>
          <button className="p-4 border border-border rounded-lg hover:bg-accent transition-colors text-left">
            <h3 className="font-semibold mb-1">Run Workflow</h3>
            <p className="text-sm text-muted-foreground">Execute automation workflow</p>
          </button>
          <button className="p-4 border border-border rounded-lg hover:bg-accent transition-colors text-left">
            <h3 className="font-semibold mb-1">Create USB</h3>
            <p className="text-sm text-muted-foreground">Make bootable USB drive</p>
          </button>
          <button className="p-4 border border-border rounded-lg hover:bg-accent transition-colors text-left">
            <h3 className="font-semibold mb-1">Generate Answer File</h3>
            <p className="text-sm text-muted-foreground">Create autounattend.xml</p>
          </button>
        </div>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">System Status</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">API Status</span>
            <span className="text-green-500 font-semibold">Connected</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">DISM Version</span>
            <span className="font-semibold">10.0.26100</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-muted-foreground">Working Directory</span>
            <span className="font-mono text-sm">C:\DeployForge\Work</span>
          </div>
        </div>
      </div>
    </div>
  );
}
