Output recordings/delete_empty_dirs_aurora.gif
Set Shell "bash"
Set FontFamily "FiraCode Nerd Font"
Set FontSize 18
Set Width 120
Set Height 34
Set CursorBlink true
Set Theme {
  Name "Aurora Midnight"
  Background "#0f0e17"
  Foreground "#fffffe"
  Cursor "#7f5af0"
  Bold "#fffffe"
  SelectionBackground "#232946"
  SelectionForeground "#fffffe"
  Black "#121629"
  Red "#ef4565"
  Green "#2cb67d"
  Yellow "#ecd444"
  Blue "#7f5af0"
  Magenta "#c620a7"
  Cyan "#2cb7c7"
  White "#fffffe"
  BrightBlack "#1c1a38"
  BrightRed "#ff6f91"
  BrightGreen "#7bd882"
  BrightYellow "#f9e784"
  BrightBlue "#a786ff"
  BrightMagenta "#ff8fcb"
  BrightCyan "#5cd4e8"
  BrightWhite "#f7f7ff"
}

Type "cd /Users/clayboss/projects/utilities_delete_empty_folder_paths"
Enter
Type "clear"
Enter
Sleep 500ms

Type "rm -rf /tmp/ded_theme && mkdir -p /tmp/ded_theme/empty /tmp/ded_theme/only_log /tmp/ded_theme/keep && touch /tmp/ded_theme/keep/stay.txt"
Enter
Sleep 600ms

Type "printf '/tmp/ded_theme/only_log\n/tmp/ded_theme/keep\n' > /tmp/ded_theme/paths.txt"
Enter
Sleep 500ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --log /tmp/ded_theme/run.jsonl /tmp/ded_theme/empty --from-file /tmp/ded_theme/paths.txt"
Enter
Sleep 4s

Type "ls -1 /tmp/ded_theme"
Enter
Sleep 3s

Type "cat /tmp/ded_theme/run.jsonl"
Enter
Sleep 4s

Type "rm -rf /tmp/ded_theme"
Enter
Sleep 1s
