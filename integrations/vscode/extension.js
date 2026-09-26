const vscode = require("vscode");
const cp = require("child_process");
const path = require("path");

function runSilab(args, cwd) {
  return new Promise((resolve, reject) => {
    const proc = cp.spawn("python", ["-m", "invariant_lab.cli.main", ...args], {
      cwd,
      shell: false
    });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", d => stdout += d.toString());
    proc.stderr.on("data", d => stderr += d.toString());
    proc.on("error", reject);
    proc.on("close", code => resolve({ code, stdout, stderr }));
  });
}

async function scanWorkspace() {
  const folder = vscode.workspace.workspaceFolders?.[0];
  if (!folder) {
    vscode.window.showErrorMessage("Open a workspace first.");
    return;
  }
  const root = folder.uri.fsPath;
  const result = await runSilab(["scan", root, "--out", ".silab/vscode"], root);
  const text = result.stdout || result.stderr;
  if (result.code === 0) {
    vscode.window.showInformationMessage("SIL scan completed.");
    const report = vscode.Uri.file(path.join(root, ".silab", "vscode", "report.html"));
    await vscode.env.openExternal(report);
  } else {
    vscode.window.showErrorMessage("SIL scan failed. See Output for details.");
  }
  const channel = vscode.window.createOutputChannel("Security Invariant Lab");
  channel.appendLine(text);
  channel.show(true);
}

async function openReport() {
  const folder = vscode.workspace.workspaceFolders?.[0];
  if (!folder) return;
  const report = vscode.Uri.file(path.join(folder.uri.fsPath, ".silab", "vscode", "report.html"));
  await vscode.env.openExternal(report);
}

function activate(context) {
  context.subscriptions.push(
    vscode.commands.registerCommand("silab.scanWorkspace", scanWorkspace),
    vscode.commands.registerCommand("silab.openReport", openReport)
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
