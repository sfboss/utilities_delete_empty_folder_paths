Set Shell "bash"
Set FontFamily "JetBrainsMono Nerd Font"
Set FontSize 18
Set Width 1920
Set Height 200
Set CursorBlink false
Set Theme {
  "name": "Nebula Overview",
  "background": "#0b1021",
  "foreground": "#f5f6ff",
  "cursor": "#58e1ff",
  "bold": "#f5f6ff",
  "selectionBackground": "#14213d",
  "selectionForeground": "#f5f6ff",
  "black": "#070a18",
  "red": "#ef476f",
  "green": "#06d6a0",
  "yellow": "#ffd166",
  "blue": "#118ab2",
  "magenta": "#7b2cbf",
  "cyan": "#4cc9f0",
  "white": "#f8f9fa",
  "brightBlack": "#1e233a",
  "brightRed": "#ff5d8f",
  "brightGreen": "#4ef5bf",
  "brightYellow": "#ffe28a",
  "brightBlue": "#4ba6d6",
  "brightMagenta": "#b37aff",
  "brightCyan": "#63e6ff",
  "brightWhite": "#ffffff"
}

Type "cd {{PROJECT_ROOT}}"
Enter
Type "clear"
Enter
Sleep 600ms

Type "echo ':: Nebula Overview ::'"
Enter
Sleep 500ms

Type "ls -1"
Enter
Sleep 1.5s

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --version"
Enter
Sleep 2s

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --no-log --help | head -n 12"
Enter
Sleep 4s

Type "echo 'Templates available:'"
Enter
Sleep 400ms

Type "ls -1 templates"
Enter
Sleep 2s
