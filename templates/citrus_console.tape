Set Shell "bash"
Set FontFamily "FiraCode Nerd Font"
Set FontSize 18
Set Width 1920
Set Height 120
Set CursorBlink true
Set Theme {
  "name": "Citrus Console",
  "background": "#1b1d1f",
  "foreground": "#f6f7eb",
  "cursor": "#ffb400",
  "bold": "#f6f7eb",
  "selectionBackground": "#2d2f31",
  "selectionForeground": "#fffbf7",
  "black": "#252525",
  "red": "#ff6b6b",
  "green": "#6bcf6b",
  "yellow": "#ffd166",
  "blue": "#118ab2",
  "magenta": "#fb6f92",
  "cyan": "#38d9a9",
  "white": "#f6f7eb",
  "brightBlack": "#3a3c3f",
  "brightRed": "#ff8787",
  "brightGreen": "#8df59a",
  "brightYellow": "#ffe066",
  "brightBlue": "#4e97d9",
  "brightMagenta": "#ff99c8",
  "brightCyan": "#66f7d3",
  "brightWhite": "#ffffff"
}

Type "cd {{PROJECT_ROOT}}"
Enter
Type "clear"
Enter
Sleep 400ms

Type "echo 'Fresh citrus cleanup run'"
Enter
Sleep 400ms

Type "rm -rf /tmp/ded_citrus && mkdir -p /tmp/ded_citrus/keep_me /tmp/ded_citrus/remove_me"
Enter
Sleep 500ms

Type "touch /tmp/ded_citrus/keep_me/notes.txt"
Enter
Sleep 400ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --no-log /tmp/ded_citrus/remove_me /tmp/ded_citrus/keep_me"
Enter
Sleep 4s

Type "ls -1 /tmp/ded_citrus"
Enter
Sleep 2s

Type "rm -rf /tmp/ded_citrus"
Enter
Sleep 600ms
