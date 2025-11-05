export default function Workflows() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Workflows</h1>
        <p className="text-muted-foreground">Automate image customization with workflows</p>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Available Workflows</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {['Gaming Optimized', 'Enterprise Hardened', 'Minimal/Tiny11', 'Developer Workstation'].map(
            (workflow) => (
              <div key={workflow} className="p-4 border border-border rounded-lg">
                <h3 className="font-semibold mb-2">{workflow}</h3>
                <p className="text-sm text-muted-foreground mb-4">Pre-configured workflow template</p>
                <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                  Execute
                </button>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}
