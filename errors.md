Rendering templates to: /Users/clayboss/projects/utilities_delete_empty_folder_paths/recordings/generated
:: Running citrus_console.tape
Set Shell bash
Set FontFamily FiraCode Nerd Font
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
Type cd /Users/clayboss/projects/utilities_delete_empty_folder_paths
Enter 1
Type clear
Enter 1
Sleep 400ms
Type echo 'Fresh citrus cleanup run'
Enter 1
Sleep 400ms
Type rm -rf /tmp/ded_citrus && mkdir -p /tmp/ded_citrus/keep_me /tmp/ded_citrus/remove_me
Enter 1
Sleep 500ms
Type touch /tmp/ded_citrus/keep_me/notes.txt
Enter 1
Sleep 400ms
Type PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --no-log /tmp/ded_citrus/remove_me /tmp/ded_citrus/keep_me
Enter 1
Sleep 4s
Type ls -1 /tmp/ded_citrus
Enter 1
Sleep 2s
Type rm -rf /tmp/ded_citrus
Enter 1
Sleep 600ms
:: Running forest_glow.tape
Set Shell bash
Set FontFamily MesloLGS NF
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
Type cd /Users/clayboss/projects/utilities_delete_empty_folder_paths
Enter 1
Type clear
Enter 1
Sleep 500ms
Type echo 'Forest glow audit run'
Enter 1
Sleep 400ms
Type rm -rf /tmp/ded_forest && mkdir -p /tmp/ded_forest/a /tmp/ded_forest/b
Enter 1
Sleep 500ms
Type touch /tmp/ded_forest/b/keep.md
Enter 1
Sleep 400ms
Type PYTHONPATH=src python3 -m delete_empty_dirs.cli --no-rich --log /tmp/ded_forest/log.jsonl /tmp/ded_forest/a /tmp/ded_forest/b
Enter 1
Sleep 4s
Type tail -n 2 /tmp/ded_forest/log.jsonl
Enter 1
Sleep 3s
Type rm -rf /tmp/ded_forest
Enter 1
Sleep 600ms
:: Running nebula_overview.tape
Set Shell bash
Set FontFamily JetBrainsMono Nerd Font
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
Type cd /Users/clayboss/projects/utilities_delete_empty_folder_paths
