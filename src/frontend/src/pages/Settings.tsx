export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground">Configure DeployForge preferences</p>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Application Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Theme</label>
            <select className="w-full px-3 py-2 bg-background border border-border rounded-lg">
              <option value="dark">Dark</option>
              <option value="light">Light</option>
              <option value="system">System</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">API Base URL</label>
            <input
              type="text"
              value="http://localhost:5000"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              readOnly
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Working Directory</label>
            <input
              type="text"
              value="C:\DeployForge\Work"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg"
              readOnly
            />
          </div>
        </div>
      </div>
    </div>
  );
}
