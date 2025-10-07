Output recordings/delete_empty_dirs_run.gif
Set Shell "bash"
Set FontSize 18
Set Theme "Dracula"
Set Width 120
Set Height 34

Type "cd /Users/clayboss/projects/utilities_delete_empty_folder_paths"
Enter
Type "clear"
Enter
Sleep 500ms

Type "rm -rf /tmp/ded_demo && mkdir -p /tmp/ded_demo/empty /tmp/ded_demo/nonempty /tmp/ded_demo/also_empty && touch /tmp/ded_demo/nonempty/file.txt"
Enter
Sleep 500ms

Type "printf '/tmp/ded_demo/also_empty\n/tmp/ded_demo/nonempty\n' > /tmp/ded_demo/paths.txt"
Enter
Sleep 500ms

Type "PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --no-log /tmp/ded_demo/empty --from-file /tmp/ded_demo/paths.txt"
Enter
Sleep 4s

Type "ls -1 /tmp/ded_demo"
Enter
Sleep 3s

Type "rm -rf /tmp/ded_demo"
Enter
Sleep 1s
