Set Shell "bash"
Set FontFamily "Hack Nerd Font"
Set FontSize 17
Set Width 1920
Set Height 290
Set CursorBlink true
Set Theme {
  "name": "Neon Grid",
  "background": "#050208",
  "foreground": "#f3f3fb",
  "cursor": "#ff00ff",
  "bold": "#f3f3fb",
  "selectionBackground": "#160b1c",
  "selectionForeground": "#f3f3fb",
  "black": "#0a0312",
  "red": "#ff206e",
  "green": "#2ceaa3",
  "yellow": "#fecd1a",
  "blue": "#683bff",
  "magenta": "#ff66c4",
  "cyan": "#2de2e6",
  "white": "#f3f3fb",
  "brightBlack": "#1a0b23",
  "brightRed": "#ff4d94",
  "brightGreen": "#60f4c3",
  "brightYellow": "#ffe162",
  "brightBlue": "#8f6bff",
  "brightMagenta": "#ff8adf",
  "brightCyan": "#5af4f9",
  "brightWhite": "#ffffff"
}

Type "cd {{PROJECT_ROOT}}"
Enter
Type "clear"
Enter
Sleep 400ms

Type "printf 'Neon grid quick help -> logs -> cleanup\\n'"
Enter
Sleep 400ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --no-log --help | sed -n '1,6p'"
Enter
Sleep 3s

Type "echo 'Current VHS recordings:'"
Enter
Sleep 400ms

Type "ls -1 recordings"
Enter
Sleep 2s

Type "echo 'Template gallery:'"
Enter
Sleep 400ms

Type "ls -1 templates"
Enter
Sleep 2s
