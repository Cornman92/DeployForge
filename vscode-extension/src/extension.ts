import * as vscode from 'vscode';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export function activate(context: vscode.ExtensionContext) {
    console.log('DeployForge extension is now active');

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('deployforge.buildImage', buildImage),
        vscode.commands.registerCommand('deployforge.analyzeImage', analyzeImage),
        vscode.commands.registerCommand('deployforge.validateImage', validateImage),
        vscode.commands.registerCommand('deployforge.compareImages', compareImages),
        vscode.commands.registerCommand('deployforge.applyProfile', applyProfile),
        vscode.commands.registerCommand('deployforge.createPreset', createPreset),
        vscode.commands.registerCommand('deployforge.listProfiles', listProfiles),
        vscode.commands.registerCommand('deployforge.listPresets', listPresets),
        vscode.commands.registerCommand('deployforge.openReport', openReport)
    );

    // Register tree data providers
    const profilesProvider = new ProfilesProvider();
    vscode.window.registerTreeDataProvider('deployforgeProfiles', profilesProvider);

    const presetsProvider = new PresetsProvider();
    vscode.window.registerTreeDataProvider('deployforgePresets', presetsProvider);

    const imagesProvider = new ImagesProvider();
    vscode.window.registerTreeDataProvider('deployforgeImages', imagesProvider);

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = "$(package) DeployForge";
    statusBarItem.command = 'deployforge.buildImage';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    showWelcomeMessage();
}

async function buildImage() {
    try {
        const config = vscode.workspace.getConfiguration('deployforge');

        // Select source image
        const imageUri = await vscode.window.showOpenDialog({
            canSelectFiles: true,
            canSelectFolders: false,
            canSelectMany: false,
            filters: { 'Windows Images': ['wim', 'esd'] },
            title: 'Select Source Windows Image'
        });

        if (!imageUri || imageUri.length === 0) {
            return;
        }

        const imagePath = imageUri[0].fsPath;

        // Select profile
        const profiles = ['gamer', 'developer', 'enterprise', 'student', 'creator', 'custom'];
        const profile = await vscode.window.showQuickPick(profiles, {
            placeHolder: 'Select a profile',
            title: 'DeployForge Profile'
        });

        if (!profile) {
            return;
        }

        // Select output location
        const outputUri = await vscode.window.showSaveDialog({
            filters: { 'Windows Images': ['wim'] },
            defaultUri: vscode.Uri.file('custom.wim'),
            title: 'Save Customized Image As'
        });

        if (!outputUri) {
            return;
        }

        const outputPath = outputUri.fsPath;

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Building ${profile} image...`,
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });

            const pythonPath = config.get<string>('pythonPath', 'python');
            const command = `${pythonPath} -m deployforge.cli build "${imagePath}" --profile ${profile} --output "${outputPath}"`;

            try {
                progress.report({ increment: 30, message: 'Applying profile...' });
                const { stdout, stderr } = await execAsync(command);

                progress.report({ increment: 60, message: 'Finalizing...' });

                if (config.get<boolean>('autoValidate', true)) {
                    await validateImageInternal(outputPath);
                }

                progress.report({ increment: 100 });

                vscode.window.showInformationMessage(
                    `✅ Image built successfully: ${path.basename(outputPath)}`,
                    'Open Folder',
                    'Analyze'
                ).then(selection => {
                    if (selection === 'Open Folder') {
                        vscode.commands.executeCommand('revealFileInOS', outputUri);
                    } else if (selection === 'Analyze') {
                        analyzeImageInternal(outputPath);
                    }
                });
            } catch (error: any) {
                vscode.window.showErrorMessage(`Build failed: ${error.message}`);
            }
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function analyzeImage(uri?: vscode.Uri) {
    const imagePath = await getImagePath(uri);
    if (!imagePath) {
        return;
    }

    await analyzeImageInternal(imagePath);
}

async function analyzeImageInternal(imagePath: string) {
    const config = vscode.workspace.getConfiguration('deployforge');
    const reportFormat = config.get<string>('reportFormat', 'html');

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Analyzing image...',
        cancellable: false
    }, async (progress) => {
        progress.report({ increment: 0 });

        const pythonPath = config.get<string>('pythonPath', 'python');
        const reportPath = path.join(path.dirname(imagePath), `analysis-report.${reportFormat}`);
        const command = `${pythonPath} -m deployforge.cli analyze "${imagePath}" --format ${reportFormat} --output "${reportPath}"`;

        try {
            const { stdout, stderr } = await execAsync(command);

            progress.report({ increment: 100 });

            vscode.window.showInformationMessage(
                '✅ Analysis complete',
                'Open Report'
            ).then(selection => {
                if (selection === 'Open Report') {
                    const reportUri = vscode.Uri.file(reportPath);
                    if (reportFormat === 'html') {
                        vscode.env.openExternal(reportUri);
                    } else {
                        vscode.workspace.openTextDocument(reportUri).then(doc => {
                            vscode.window.showTextDocument(doc);
                        });
                    }
                }
            });
        } catch (error: any) {
            vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
        }
    });
}

async function validateImage(uri?: vscode.Uri) {
    const imagePath = await getImagePath(uri);
    if (!imagePath) {
        return;
    }

    await validateImageInternal(imagePath);
}

async function validateImageInternal(imagePath: string) {
    const config = vscode.workspace.getConfiguration('deployforge');

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Validating image...',
        cancellable: false
    }, async (progress) => {
        progress.report({ increment: 0 });

        const pythonPath = config.get<string>('pythonPath', 'python');
        const command = `${pythonPath} -m deployforge.cli validate "${imagePath}"`;

        try {
            const { stdout, stderr } = await execAsync(command);

            progress.report({ increment: 100 });

            vscode.window.showInformationMessage('✅ Validation passed');
        } catch (error: any) {
            vscode.window.showWarningMessage('⚠️ Validation failed - see output for details');
        }
    });
}

async function compareImages() {
    const image1Uri = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { 'Windows Images': ['wim', 'esd'] },
        title: 'Select First Image'
    });

    if (!image1Uri || image1Uri.length === 0) {
        return;
    }

    const image2Uri = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { 'Windows Images': ['wim', 'esd'] },
        title: 'Select Second Image'
    });

    if (!image2Uri || image2Uri.length === 0) {
        return;
    }

    const config = vscode.workspace.getConfiguration('deployforge');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const command = `${pythonPath} -m deployforge.cli diff "${image1Uri[0].fsPath}" "${image2Uri[0].fsPath}"`;

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Comparing images...',
        cancellable: false
    }, async (progress) => {
        try {
            const { stdout, stderr } = await execAsync(command);

            // Show results in output channel
            const outputChannel = vscode.window.createOutputChannel('DeployForge Comparison');
            outputChannel.appendLine('=== Image Comparison ===');
            outputChannel.appendLine(stdout);
            outputChannel.show();

            vscode.window.showInformationMessage('✅ Comparison complete - see output');
        } catch (error: any) {
            vscode.window.showErrorMessage(`Comparison failed: ${error.message}`);
        }
    });
}

async function applyProfile(uri?: vscode.Uri) {
    const imagePath = await getImagePath(uri);
    if (!imagePath) {
        return;
    }

    const profiles = ['gamer', 'developer', 'enterprise', 'student', 'creator', 'custom'];
    const profile = await vscode.window.showQuickPick(profiles, {
        placeHolder: 'Select a profile to apply',
        title: 'DeployForge Profile'
    });

    if (!profile) {
        return;
    }

    const config = vscode.workspace.getConfiguration('deployforge');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const command = `${pythonPath} -m deployforge.cli apply-profile ${profile}`;

    await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: `Applying ${profile} profile...`,
        cancellable: false
    }, async (progress) => {
        try {
            const { stdout, stderr } = await execAsync(command);
            vscode.window.showInformationMessage(`✅ Profile applied: ${profile}`);
        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to apply profile: ${error.message}`);
        }
    });
}

async function createPreset() {
    const name = await vscode.window.showInputBox({
        prompt: 'Enter preset name',
        placeHolder: 'My Custom Preset'
    });

    if (!name) {
        return;
    }

    const profiles = ['gamer', 'developer', 'enterprise', 'student', 'creator', 'custom', 'None'];
    const baseProfile = await vscode.window.showQuickPick(profiles, {
        placeHolder: 'Select base profile (optional)',
        title: 'Base Profile'
    });

    const config = vscode.workspace.getConfiguration('deployforge');
    const pythonPath = config.get<string>('pythonPath', 'python');
    let command = `${pythonPath} -m deployforge.cli create-preset "${name}"`;

    if (baseProfile && baseProfile !== 'None') {
        command += ` --base ${baseProfile}`;
    }

    try {
        const { stdout, stderr } = await execAsync(command);
        vscode.window.showInformationMessage(`✅ Preset created: ${name}`);
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to create preset: ${error.message}`);
    }
}

async function listProfiles() {
    const config = vscode.workspace.getConfiguration('deployforge');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const command = `${pythonPath} -m deployforge.cli list-profiles`;

    try {
        const { stdout, stderr } = await execAsync(command);
        const outputChannel = vscode.window.createOutputChannel('DeployForge Profiles');
        outputChannel.appendLine('=== Available Profiles ===');
        outputChannel.appendLine(stdout);
        outputChannel.show();
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list profiles: ${error.message}`);
    }
}

async function listPresets() {
    const config = vscode.workspace.getConfiguration('deployforge');
    const pythonPath = config.get<string>('pythonPath', 'python');
    const command = `${pythonPath} -m deployforge.cli list-presets`;

    try {
        const { stdout, stderr } = await execAsync(command);
        const outputChannel = vscode.window.createOutputChannel('DeployForge Presets');
        outputChannel.appendLine('=== Available Presets ===');
        outputChannel.appendLine(stdout);
        outputChannel.show();
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to list presets: ${error.message}`);
    }
}

async function openReport() {
    const reportUri = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { 'Reports': ['html', 'json', 'txt'] },
        title: 'Select Report File'
    });

    if (!reportUri || reportUri.length === 0) {
        return;
    }

    const reportPath = reportUri[0].fsPath;
    const ext = path.extname(reportPath).toLowerCase();

    if (ext === '.html') {
        vscode.env.openExternal(reportUri[0]);
    } else {
        const doc = await vscode.workspace.openTextDocument(reportPath);
        vscode.window.showTextDocument(doc);
    }
}

async function getImagePath(uri?: vscode.Uri): Promise<string | undefined> {
    if (uri) {
        return uri.fsPath;
    }

    const result = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { 'Windows Images': ['wim', 'esd'] },
        title: 'Select Windows Image'
    });

    if (!result || result.length === 0) {
        return undefined;
    }

    return result[0].fsPath;
}

function showWelcomeMessage() {
    const config = vscode.workspace.getConfiguration('deployforge');
    if (config.get<boolean>('showNotifications', true)) {
        vscode.window.showInformationMessage(
            'DeployForge extension loaded!',
            'Build Image',
            'View Profiles'
        ).then(selection => {
            if (selection === 'Build Image') {
                vscode.commands.executeCommand('deployforge.buildImage');
            } else if (selection === 'View Profiles') {
                vscode.commands.executeCommand('deployforge.listProfiles');
            }
        });
    }
}

// Tree data providers
class ProfilesProvider implements vscode.TreeDataProvider<ProfileItem> {
    getTreeItem(element: ProfileItem): vscode.TreeItem {
        return element;
    }

    getChildren(): Thenable<ProfileItem[]> {
        const profiles = [
            new ProfileItem('Gamer', 'Gaming optimizations', 'gamer'),
            new ProfileItem('Developer', 'Development tools', 'developer'),
            new ProfileItem('Enterprise', 'Enterprise features', 'enterprise'),
            new ProfileItem('Student', 'Student edition', 'student'),
            new ProfileItem('Creator', 'Content creation', 'creator'),
            new ProfileItem('Custom', 'Custom configuration', 'custom')
        ];
        return Promise.resolve(profiles);
    }
}

class ProfileItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string,
        public readonly profileName: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = description;
        this.contextValue = 'profile';
        this.command = {
            command: 'deployforge.applyProfile',
            title: 'Apply Profile',
            arguments: [profileName]
        };
    }
}

class PresetsProvider implements vscode.TreeDataProvider<PresetItem> {
    getTreeItem(element: PresetItem): vscode.TreeItem {
        return element;
    }

    getChildren(): Thenable<PresetItem[]> {
        // In a real implementation, this would fetch presets from the system
        const presets: PresetItem[] = [];
        return Promise.resolve(presets);
    }
}

class PresetItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly description: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = description;
        this.contextValue = 'preset';
    }
}

class ImagesProvider implements vscode.TreeDataProvider<ImageItem> {
    getTreeItem(element: ImageItem): vscode.TreeItem {
        return element;
    }

    getChildren(): Thenable<ImageItem[]> {
        // In a real implementation, this would scan for WIM files in workspace
        const images: ImageItem[] = [];
        return Promise.resolve(images);
    }
}

class ImageItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly imagePath: string
    ) {
        super(label, vscode.TreeItemCollapsibleState.None);
        this.tooltip = imagePath;
        this.contextValue = 'image';
        this.resourceUri = vscode.Uri.file(imagePath);
    }
}

export function deactivate() {
    console.log('DeployForge extension is now deactivated');
}
