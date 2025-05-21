#!/bin/bash
set -e

# Check arguments
if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <input_markdown_file> <output_png_path>"
  exit 1
fi

# Input parameters
INPUT_FILE="$1"
OUTPUT_PNG="$2"
TEMP_BASE_NAME=$(basename "$INPUT_FILE" .md)
TEMP_DIR="$(dirname "$OUTPUT_PNG")/temp_${TEMP_BASE_NAME}_$$_$(date +%s)"

# Create temp directory
mkdir -p "$TEMP_DIR"

# Function to count words in markdown file
count_words() {
  local file=$1
  # Remove code blocks and count remaining words
  cat "$file" | sed '/^```/,/^```/d' | wc -w
}

# Function to determine optimal page count
determine_page_count() {
  local word_count=$1
  
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
  # Ensure lines_per_section is at least 1, handle total_lines < total_sections
  if [ "$total_lines" -le 1 ]; then # If only title or title + 1 line content
    total_lines_for_calc=$((total_sections + 1)) # ensure lines_per_section is at least 1
  else
    total_lines_for_calc=$total_lines
  fi
  local lines_per_section=$(( (total_lines_for_calc - 1) / total_sections ))
  [ "$lines_per_section" -lt 1 ] && lines_per_section=1 # Ensure at least 1 line per section

  local start_line=$(( 2 + (section_num - 1) * lines_per_section ))
  # If first section and only one section, start from line 1 to include title if not handled by echo h1
  if [ "$section_num" -eq 1 ] && [ "$total_sections" -eq 1 ]; then
    start_line=1
  elif [ "$section_num" -eq 1 ]; then # For multi-section, first section content starts after title
    start_line=2
  fi

  local end_line=$(( start_line + lines_per_section - 1 ))
  [ "$start_line" -gt "$total_lines" ] && start_line=$total_lines # cap start_line

  # Smarter splitting (simplified from your original, as it was complex and error-prone)
  # This simple split is okay for now, can be improved if section breaks are bad.

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
      max-width: 800px; /* Ensure consistent width for image conversion */
      min-height: 1000px; /* Approximate A4 height for 800px width, adjust as needed */
      box-sizing: border-box;
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
  
  # Extract section content using pandoc directly on the segment
  # This requires a way to pass content segments to pandoc. 
  # Simpler: use pandoc on whole file and then CSS for page breaks if possible, 
  # or stick to line-based segmentation if pandoc can't easily take segments.
  # For now, keeping line-based segmentation for pandoc input for simplicity with current structure.
  
  temp_md_section="${TEMP_DIR}/temp_section_${section_num}.md"
  if [ "$section_num" -eq 1 ] && [ "$total_sections" -eq 1 ]; then # Single section means whole file content after title
    tail -n +2 "$md_file" > "$temp_md_section" # Assumes title is only first line
  elif [ "$section_num" -eq 1 ]; then # First of multiple sections
    sed -n "${start_line},${end_line}p" "$md_file" > "$temp_md_section"
  elif [ "$section_num" -eq "$total_sections" ]; then # Last section
    sed -n "${start_line},\$p" "$md_file" > "$temp_md_section"
  else # Middle sections
    sed -n "${start_line},${end_line}p" "$md_file" > "$temp_md_section"
  fi

  pandoc -f markdown -t html "$temp_md_section" >> "$output_file"
  rm "$temp_md_section"
  
  # Add page number
  echo "<div class='page-number'>Page ${section_num} of ${total_sections}</div>" >> "$output_file"
  
  # Close HTML
  echo "</body></html>" >> "$output_file"
}

# Process the markdown file
echo "Processing $(basename "$INPUT_FILE")..."

# Count words in the file
word_count=$(count_words "$INPUT_FILE")
echo "  Word count: $word_count"

# Determine optimal page count
page_count=$(determine_page_count "$word_count")
echo "  Splitting into $page_count page(s)"

# Create HTML sections
declare -a section_pngs

for ((i=1; i<=page_count; i++)); do
  section_html="$TEMP_DIR/section_${i}.html"
  create_section_html "$INPUT_FILE" $i $page_count "$section_html"
  
  section_png_path="$TEMP_DIR/section_${i}.png"
  section_pngs+=("$section_png_path") # Add to array

  # Convert HTML to image
  echo "  Converting section $i to image..."
  if command -v wkhtmltoimage &> /dev/null; then
    xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" wkhtmltoimage --quiet --quality 100 --width 800 --enable-local-file-access "$section_html" "$section_png_path"
    if [ ! -f "$section_png_path" ] || [ ! -s "$section_png_path" ]; then # Check if file exists and is not empty
      echo "Error: wkhtmltoimage failed to create a valid image for section $i ($section_png_path)"
      # Attempting ImageMagick convert as a fallback
      if command -v convert &> /dev/null; then
        echo "    wkhtmltoimage failed. Attempting fallback using ImageMagick convert..."
        convert -size 800x6000 xc:white -draw "text 0,0 '$(cat "$section_html" | tr -d '\n' | sed -e "s/'//g" -e 's/[\"\\"]//g')" -trim "$section_png_path"
        if [ ! -f "$section_png_path" ] || [ ! -s "$section_png_path" ]; then
          echo "Error: ImageMagick convert fallback also failed to create a valid image for section $i ($section_png_path)"
          rm -rf "$TEMP_DIR"
          exit 1
        fi
      else
        echo "Error: ImageMagick convert not found for fallback."
        rm -rf "$TEMP_DIR"
        exit 1
      fi
    fi
  elif command -v convert &> /dev/null; then # Fallback to ImageMagick (less ideal for HTML) if wkhtmltoimage not present at all
    echo "    wkhtmltoimage not found. Using ImageMagick convert (may have formatting issues for complex HTML)"
    # This is a very basic conversion and might not render HTML well.
    # For better results with `convert`, one might need to use `html2ps` then `ps2png` or use a browser engine like puppeteer.
    # Forcing a large height to try and capture content, then trim.
    convert -size 800x6000 xc:white -draw "text 0,0 '$(cat "$section_html" | tr -d '\n' | sed -e "s/'//g" -e 's/[\"\\"]//g')" -trim "$section_png_path"
    # The above ImageMagick convert command for HTML is highly experimental and likely to fail or produce poor results.
    # wkhtmltoimage is strongly preferred.
  else
    echo "Error: No suitable HTML-to-image converter found!"
    echo "Please install wkhtmltoimage (recommended) or ImageMagick (less reliable for HTML)."
    # Clean up temp before exiting
    rm -rf "$TEMP_DIR"
    exit 1
  fi
  echo "    Section $i image created: $section_png_path"
done

# Determine optimal layout and create final image
echo "  Assembling final poster from $page_count section(s)..."
if [ "$page_count" -eq 1 ]; then
  # Single page - just copy it
  cp "${section_pngs[0]}" "$OUTPUT_PNG"
elif [ "$page_count" -eq 2 ]; then
  # Two pages - side by side
  convert "${section_pngs[0]}" "${section_pngs[1]}" +append "$OUTPUT_PNG"
elif [ "$page_count" -eq 4 ]; then
  # Four pages - 2x2 grid
  montage "${section_pngs[0]}" "${section_pngs[1]}" \
          "${section_pngs[2]}" "${section_pngs[3]}" \
          -geometry +5+5 -tile 2x2 "$OUTPUT_PNG"
elif [ "$page_count" -eq 6 ]; then
  # Six pages - 3x2 grid
  montage "${section_pngs[0]}" "${section_pngs[1]}" "${section_pngs[2]}" \
          "${section_pngs[3]}" "${section_pngs[4]}" "${section_pngs[5]}" \
          -geometry +5+5 -tile 3x2 "$OUTPUT_PNG"
elif [ "$page_count" -eq 9 ]; then
  # Nine pages - 3x3 grid
  montage "${section_pngs[0]}" "${section_pngs[1]}" "${section_pngs[2]}" \
          "${section_pngs[3]}" "${section_pngs[4]}" "${section_pngs[5]}" \
          "${section_pngs[6]}" "${section_pngs[7]}" "${section_pngs[8]}" \
          -geometry +5+5 -tile 3x3 "$OUTPUT_PNG"
fi

echo "  Created $OUTPUT_PNG"

# Clean up temporary files
rm -rf "$TEMP_DIR"

echo "Done! Poster saved to $OUTPUT_PNG"
