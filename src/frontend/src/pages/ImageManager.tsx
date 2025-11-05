export default function ImageManager() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Image Manager</h1>
        <p className="text-muted-foreground">Mount and manage Windows image files</p>
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Mounted Images</h2>
        <div className="text-center py-12 text-muted-foreground">
          <p>No images mounted</p>
          <button className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
            Mount Image
          </button>
        </div>
      </div>
    </div>
  );
}
