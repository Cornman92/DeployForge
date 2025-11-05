export default function Deployment() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Deployment</h1>
        <p className="text-muted-foreground">Create bootable media and answer files</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">USB Bootable Creation</h3>
          <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            Create Bootable USB
          </button>
        </div>

        <div className="bg-card border border-border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">Autounattend Generator</h3>
          <button className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            Generate Answer File
          </button>
        </div>
      </div>
    </div>
  );
}
