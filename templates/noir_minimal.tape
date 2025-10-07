Set Shell "bash"
Set FontFamily "IBMPlexMono"
Set FontSize 17
Set Width 1920
Set Height 320
Set CursorBlink false
Set Theme {
  "name": "Noir Minimal",
  "background": "#08090c",
  "foreground": "#d9d7ce",
  "cursor": "#f2f2f2",
  "bold": "#f2f2f2",
  "selectionBackground": "#1a1c23",
  "selectionForeground": "#ffffff",
  "black": "#0f1115",
  "red": "#ff4a57",
  "green": "#4caf50",
  "yellow": "#ffb400",
  "blue": "#1e90ff",
  "magenta": "#b980f0",
  "cyan": "#4dd0e1",
  "white": "#d9d7ce",
  "brightBlack": "#1c1f26",
  "brightRed": "#ff6b73",
  "brightGreen": "#7edc82",
  "brightYellow": "#ffd369",
  "brightBlue": "#4ab0ff",
  "brightMagenta": "#d6a6ff",
  "brightCyan": "#7be0f4",
  "brightWhite": "#ffffff"
}

Type "cd {{PROJECT_ROOT}}"
Enter
Type "clear"
Enter
Sleep 500ms

Type "printf ':: Minimal policy report ::\n'"
Enter
Sleep 400ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --restrict-to {{PROJECT_ROOT}} --no-rich --no-log README.md"
Enter
Sleep 3s

Type "printf '\\nAvailable logs (if any):\\n'"
Enter
Sleep 400ms

Type "ls -1 .project_logs 2>/dev/null || echo '(no logs yet)'"
Enter
Sleep 2s
