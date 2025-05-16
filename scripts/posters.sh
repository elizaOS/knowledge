#!/bin/bash
set -e

# Check arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <markdown_directory> <output_directory>"
  echo "  Will automatically create optimal layout based on content length"
  exit 1
fi

# Input parameters
MD_DIR="$1"
OUT_DIR="$2"
TEMP_DIR="$OUT_DIR/temp"

# Create output directories
mkdir -p "$OUT_DIR" "$TEMP_DIR"

# Function to count words in markdown file
count_words() {
  local file=$1
  # Remove code blocks and count remaining words
  cat "$file" | sed '/^```/,/^```/d' | wc -w
}

# Function to determine optimal page count
determine_page_count() {
  local word_count=$1
  local chars_per_page=1000
  
  # Very short content (1 page)
  if [ "$word_count" -lt 500 ]; then
    echo 1
  # Medium content (2 pages)
  elif [ "$word_count" -lt 1200 ]; then
    echo 2
  # Long content (4 pages in 2x2 grid)
  elif [ "$word_count" -lt 2500 ]; then
    echo 4
  # Very long content (6 pages in 3x2 grid)
  elif [ "$word_count" -lt 4000 ]; then
    echo 6
  # Extremely long content (9 pages in 3x3 grid)
  else
    echo 9
  fi
}

# Function to create HTML for a section of markdown
create_section_html() {
  local md_file=$1
  local section_num=$2
  local total_sections=$3
  local output_file=$4
  local title=$(head -n 1 "$md_file" | sed -E 's/^#+ //g')
  
  # Calculate approximate lines per section
  local total_lines=$(wc -l < "$md_file")
  local lines_per_section=$(( (total_lines - 1) / total_sections ))
  local start_line=$(( 2 + (section_num - 1) * lines_per_section ))
  local end_line=$(( start_line + lines_per_section - 1 ))
  
  # Adjust to avoid breaking in the middle of sections
  if [ "$section_num" -gt 1 ]; then
    # Look back for a good break point (empty line or heading)
    local i=$start_line
    while [ "$i" -gt $(( start_line - 10 )) ] && [ "$i" -gt 2 ]; do
      local line=$(sed -n "${i}p" "$md_file")
      if [[ "$line" =~ ^#+ ]] || [[ -z "$line" ]]; then
        start_line=$i
        break
      fi
      i=$(( i - 1 ))
    done
  fi
  
  if [ "$section_num" -lt "$total_sections" ]; then
    # Look forward for a good break point
    local i=$end_line
    while [ "$i" -lt $(( end_line + 10 )) ] && [ "$i" -lt "$total_lines" ]; do
      local line=$(sed -n "${i}p" "$md_file")
      if [[ "$line" =~ ^#+ ]] || [[ -z "$line" ]]; then
        end_line=$i
        break
      fi
      i=$(( i + 1 ))
    done
  fi
  
  # Create HTML for this section
  cat > "$output_file" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${title} - Part ${section_num}</title>
  <style>
    body { 
      font-family: Arial, sans-serif; 
      line-height: 1.5; 
      padding: 20px; 
      max-width: 800px; 
      margin: 0 auto; 
      background-color: white;
      color: black;
      font-size: 14px;
    }
    h1 { 
      font-size: 20px; 
      margin-top: 10px; 
      margin-bottom: 15px; 
      text-align: center;
      border-bottom: 1px solid #ccc;
      padding-bottom: 10px;
    }
    h2 { 
      font-size: 18px; 
      margin-top: 15px; 
      margin-bottom: 10px; 
      color: #222;
    }
    h3 { 
      font-size: 16px; 
      margin-top: 12px; 
      margin-bottom: 8px; 
      color: #333;
    }
    h4, h5, h6 { 
      font-size: 14px; 
      font-weight: bold; 
      margin-top: 10px; 
      margin-bottom: 5px; 
      color: #444;
    }
    p { margin: 5px 0; }
    ul, ol { margin: 5px 0; padding-left: 25px; }
    li { margin-bottom: 3px; }
    li > ul, li > ol { margin: 2px 0; }
    code { 
      font-family: monospace; 
      background-color: #f5f5f5; 
      padding: 2px 4px; 
      font-size: 90%;
      border-radius: 3px;
    }
    pre { 
      background-color: #f5f5f5; 
      padding: 8px; 
      overflow-x: auto; 
      border-radius: 4px;
      margin: 10px 0;
    }
    pre code { background: none; padding: 0; font-size: 90%; }
    strong { font-weight: bold; }
    table { 
      border-collapse: collapse; 
      width: 100%; 
      margin: 10px 0;
    }
    table, th, td { border: 1px solid #ddd; }
    th, td { padding: 5px; text-align: left; }
    th { background-color: #f5f5f5; }
    blockquote {
      margin: 10px 0;
      padding-left: 15px;
      border-left: 3px solid #ccc;
      color: #555;
    }
    .page-number {
      text-align: right;
      font-size: 12px;
      color: #777;
      margin-top: 20px;
    }
  </style>
</head>
<body>
EOF

  # Extract the main title for the first page only
  if [ "$section_num" -eq 1 ]; then
    echo "<h1>${title}</h1>" >> "$output_file"
  else
    echo "<h1>${title} (continued)</h1>" >> "$output_file"
  fi
  
  # Extract section content
  if [ "$section_num" -eq "$total_sections" ]; then
    # Last section includes everything to the end
    sed -n "${start_line},\$p" "$md_file" | pandoc -f markdown -t html >> "$output_file"
  else
    sed -n "${start_line},${end_line}p" "$md_file" | pandoc -f markdown -t html >> "$output_file"
  fi
  
  # Add page number
  echo "<div class='page-number'>Page ${section_num} of ${total_sections}</div>" >> "$output_file"
  
  # Close HTML
  echo "</body></html>" >> "$output_file"
}

# Process each markdown file
for md_file in "$MD_DIR"/*.md; do
  # Skip if not a file
  [ -f "$md_file" ] || continue
  
  # Get base filename
  base_name=$(basename "$md_file" .md)
  echo "Processing $base_name..."
  
  # Count words in the file
  word_count=$(count_words "$md_file")
  echo "  Word count: $word_count"
  
  # Determine optimal page count
  page_count=$(determine_page_count "$word_count")
  echo "  Splitting into $page_count page(s)"
  
  # Create HTML sections
  mkdir -p "$TEMP_DIR/$base_name"
  for ((i=1; i<=page_count; i++)); do
    section_html="$TEMP_DIR/$base_name/section_${i}.html"
    create_section_html "$md_file" $i $page_count "$section_html"
    
    # Convert HTML to image
    if command -v wkhtmltoimage &> /dev/null; then
      wkhtmltoimage --quiet --quality 100 --width 800 "$section_html" "$TEMP_DIR/$base_name/section_${i}.png"
    elif command -v convert &> /dev/null; then
      convert -size 800x -background white -fill black \
        -define pango:justify=true pango:"$(cat "$section_html")" "$TEMP_DIR/$base_name/section_${i}.png"
    else
      echo "Error: No suitable HTML-to-image converter found!"
      echo "Please install wkhtmltoimage or ImageMagick"
      exit 1
    fi
  done
  
  # Determine optimal layout
  if [ "$page_count" -eq 1 ]; then
    # Single page - just copy it
    cp "$TEMP_DIR/$base_name/section_1.png" "$OUT_DIR/${base_name}.png"
  elif [ "$page_count" -eq 2 ]; then
    # Two pages - side by side
    convert "$TEMP_DIR/$base_name/section_1.png" "$TEMP_DIR/$base_name/section_2.png" +append "$OUT_DIR/${base_name}.png"
  elif [ "$page_count" -eq 4 ]; then
    # Four pages - 2x2 grid
    montage "$TEMP_DIR/$base_name/section_1.png" "$TEMP_DIR/$base_name/section_2.png" \
            "$TEMP_DIR/$base_name/section_3.png" "$TEMP_DIR/$base_name/section_4.png" \
            -geometry +5+5 -tile 2x2 "$OUT_DIR/${base_name}.png"
  elif [ "$page_count" -eq 6 ]; then
    # Six pages - 3x2 grid
    montage "$TEMP_DIR/$base_name/section_1.png" "$TEMP_DIR/$base_name/section_2.png" "$TEMP_DIR/$base_name/section_3.png" \
            "$TEMP_DIR/$base_name/section_4.png" "$TEMP_DIR/$base_name/section_5.png" "$TEMP_DIR/$base_name/section_6.png" \
            -geometry +5+5 -tile 3x2 "$OUT_DIR/${base_name}.png"
  elif [ "$page_count" -eq 9 ]; then
    # Nine pages - 3x3 grid
    montage "$TEMP_DIR/$base_name/section_1.png" "$TEMP_DIR/$base_name/section_2.png" "$TEMP_DIR/$base_name/section_3.png" \
            "$TEMP_DIR/$base_name/section_4.png" "$TEMP_DIR/$base_name/section_5.png" "$TEMP_DIR/$base_name/section_6.png" \
            "$TEMP_DIR/$base_name/section_7.png" "$TEMP_DIR/$base_name/section_8.png" "$TEMP_DIR/$base_name/section_9.png" \
            -geometry +5+5 -tile 3x3 "$OUT_DIR/${base_name}.png"
  fi
  
  echo "  Created $OUT_DIR/${base_name}.png"
done

# Clean up temporary files
rm -rf "$TEMP_DIR"

echo "Done! All posters saved to $OUT_DIR"
ls -lh "$OUT_DIR"
