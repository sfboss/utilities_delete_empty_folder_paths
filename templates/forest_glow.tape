Set Shell "bash"
Set FontFamily "MesloLGS NF"
Set FontSize 18
Set Width 1920
Set Height 120
Set CursorBlink true
Set Theme {
  "name": "Forest Glow",
  "background": "#101c16",
  "foreground": "#f5fff2",
  "cursor": "#8cffc1",
  "bold": "#f5fff2",
  "selectionBackground": "#1c2b23",
  "selectionForeground": "#f5fff2",
  "black": "#14231a",
  "red": "#ff6f59",
  "green": "#4caf50",
  "yellow": "#ffe066",
  "blue": "#1b98e0",
  "magenta": "#a66cff",
  "cyan": "#5ce0d8",
  "white": "#f5fff2",
  "brightBlack": "#1f3529",
  "brightRed": "#ff8873",
  "brightGreen": "#7adf81",
  "brightYellow": "#fff38f",
  "brightBlue": "#5ab4ff",
  "brightMagenta": "#c79bff",
  "brightCyan": "#7cefe4",
  "brightWhite": "#ffffff"
}

Type "cd {{PROJECT_ROOT}}"
Enter
Type "clear"
Enter
Sleep 500ms

Type "echo 'Forest glow audit run'"
Enter
Sleep 400ms

Type "rm -rf /tmp/ded_forest && mkdir -p /tmp/ded_forest/a /tmp/ded_forest/b"
Enter
Sleep 500ms

Type "touch /tmp/ded_forest/b/keep.md"
Enter
Sleep 400ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --log /tmp/ded_forest/log.jsonl /tmp/ded_forest/a /tmp/ded_forest/b"
Enter
Sleep 4s

Type "tail -n 2 /tmp/ded_forest/log.jsonl"
Enter
Sleep 3s

Type "rm -rf /tmp/ded_forest"
Enter
Sleep 600ms
