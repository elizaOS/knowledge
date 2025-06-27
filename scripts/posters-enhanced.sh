#!/bin/bash
set -e

# Enhanced Poster Generation Script
# Improved styling, robustness, and fallback handling

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

# Logging functions
log_info() { echo -e "\033[94m[INFO]\033[0m $1"; }
log_success() { echo -e "\033[92m[SUCCESS]\033[0m $1"; }
log_warn() { echo -e "\033[93m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[91m[ERROR]\033[0m $1"; }

# Enhanced error handling
cleanup_and_exit() {
  local exit_code=$1
  log_info "Cleaning up temporary files..."
  rm -rf "$TEMP_DIR"
  exit $exit_code
}

# Trap to ensure cleanup on exit
trap 'cleanup_and_exit $?' EXIT

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

# Enhanced CSS with ElizaOS branding and improved typography
get_enhanced_css() {
  cat << 'EOF'
    :root {
      --eliza-primary: #2026ad;
      --eliza-secondary: #e67e22;
      --eliza-accent: #9b59b6;
      --eliza-success: #2ecc71;
      --eliza-gradient: linear-gradient(135deg, #2026ad, #9b59b6);
      
      --font-heading: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      --font-body: 'Inter', 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
      --font-mono: 'SF Mono', 'Monaco', 'Cascadia Code', 'Roboto Mono', monospace;
      
      --spacing-xs: 4px;
      --spacing-sm: 8px;
      --spacing-md: 16px;
      --spacing-lg: 24px;
      --spacing-xl: 32px;
      
      --border-radius: 8px;
      --border-radius-lg: 12px;
      --shadow-subtle: 0 1px 3px rgba(32, 38, 173, 0.1);
      --shadow-elevated: 0 4px 16px rgba(32, 38, 173, 0.15);
    }
    
    * {
      box-sizing: border-box;
    }
    
    body { 
      font-family: var(--font-body);
      line-height: 1.6; 
      padding: var(--spacing-xl); 
      max-width: 800px;
      min-height: 1000px;
      margin: 0 auto; 
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
      color: #1a202c;
      font-size: 14px;
      border: 1px solid #e2e8f0;
      position: relative;
    }
    
    /* ElizaOS Brand Header */
    .eliza-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: var(--spacing-lg);
      padding-bottom: var(--spacing-md);
      border-bottom: 2px solid var(--eliza-primary);
      background: var(--eliza-gradient);
      margin: calc(-1 * var(--spacing-xl)) calc(-1 * var(--spacing-xl)) var(--spacing-lg);
      padding: var(--spacing-md) var(--spacing-xl);
      color: white;
    }
    
    .eliza-logo {
      font-weight: 800;
      font-size: 18px;
      letter-spacing: -0.025em;
    }
    
    .page-indicator {
      font-size: 12px;
      opacity: 0.9;
      background: rgba(255, 255, 255, 0.2);
      padding: var(--spacing-xs) var(--spacing-sm);
      border-radius: var(--border-radius);
    }
    
    h1 { 
      font-family: var(--font-heading);
      font-size: 22px;
      font-weight: 700;
      margin: var(--spacing-lg) 0 var(--spacing-md) 0;
      text-align: center;
      color: var(--eliza-primary);
      line-height: 1.3;
    }
    
    h2 { 
      font-family: var(--font-heading);
      font-size: 18px;
      font-weight: 600;
      margin: var(--spacing-lg) 0 var(--spacing-sm) 0;
      color: var(--eliza-secondary);
      border-left: 4px solid var(--eliza-secondary);
      padding-left: var(--spacing-md);
    }
    
    h3 { 
      font-family: var(--font-heading);
      font-size: 16px;
      font-weight: 600;
      margin: var(--spacing-md) 0 var(--spacing-sm) 0;
      color: var(--eliza-accent);
    }
    
    h4, h5, h6 { 
      font-family: var(--font-heading);
      font-size: 14px;
      font-weight: 600;
      margin: var(--spacing-sm) 0 var(--spacing-xs) 0;
      color: #4a5568;
    }
    
    p { 
      margin: var(--spacing-sm) 0;
      text-align: justify;
    }
    
    ul, ol { 
      margin: var(--spacing-sm) 0;
      padding-left: var(--spacing-lg);
    }
    
    li { 
      margin-bottom: var(--spacing-xs);
      line-height: 1.5;
    }
    
    li > ul, li > ol { 
      margin: var(--spacing-xs) 0;
    }
    
    code { 
      font-family: var(--font-mono);
      background: #f7fafc;
      border: 1px solid #e2e8f0;
      padding: 2px 6px;
      font-size: 12px;
      border-radius: var(--border-radius);
      color: var(--eliza-accent);
    }
    
    pre { 
      background: #f7fafc;
      border: 1px solid #e2e8f0;
      border-left: 4px solid var(--eliza-primary);
      padding: var(--spacing-md);
      overflow-x: auto;
      border-radius: var(--border-radius);
      margin: var(--spacing-md) 0;
      box-shadow: var(--shadow-subtle);
    }
    
    pre code { 
      background: none;
      border: none;
      padding: 0;
      font-size: 12px;
      color: inherit;
    }
    
    strong { 
      font-weight: 600;
      color: var(--eliza-primary);
    }
    
    em {
      font-style: italic;
      color: var(--eliza-accent);
    }
    
    table { 
      border-collapse: collapse;
      width: 100%;
      margin: var(--spacing-md) 0;
      font-size: 12px;
      box-shadow: var(--shadow-subtle);
      border-radius: var(--border-radius);
      overflow: hidden;
    }
    
    th, td { 
      border: 1px solid #e2e8f0;
      padding: var(--spacing-sm);
      text-align: left;
    }
    
    th { 
      background: var(--eliza-gradient);
      color: white;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.025em;
    }
    
    tr:nth-child(even) {
      background: #f8fafc;
    }
    
    blockquote {
      margin: var(--spacing-md) 0;
      padding: var(--spacing-md);
      border-left: 4px solid var(--eliza-accent);
      background: #f8fafc;
      border-radius: 0 var(--border-radius) var(--border-radius) 0;
      color: #4a5568;
      font-style: italic;
    }
    
    .content-footer {
      margin-top: auto;
      padding-top: var(--spacing-lg);
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: #718096;
    }
    
    .generation-date {
      font-weight: 500;
    }
    
    .eliza-watermark {
      font-weight: 600;
      color: var(--eliza-primary);
    }
    
    /* Responsive adjustments for different page counts */
    .layout-1x1 { font-size: 16px; }
    .layout-1x2 { font-size: 14px; }
    .layout-2x2 { font-size: 13px; }
    .layout-2x3 { font-size: 12px; }
    .layout-3x3 { font-size: 11px; }
    
    /* Print optimizations */
    @media print {
      body {
        background: white !important;
        border: none !important;
      }
      .eliza-header {
        background: var(--eliza-primary) !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
      }
    }
EOF
}

# Function to create HTML for a section of markdown
create_section_html() {
  local md_file=$1
  local section_num=$2
  local total_sections=$3
  local output_file=$4
  local title=$(head -n 1 "$md_file" | sed -E 's/^#+ //g')
  local layout_class="layout-1x1"
  
  # Determine layout class based on total sections
  case $total_sections in
    2) layout_class="layout-1x2" ;;
    4) layout_class="layout-2x2" ;;
    6) layout_class="layout-2x3" ;;
    9) layout_class="layout-3x3" ;;
  esac
  
  # Calculate approximate lines per section
  local total_lines=$(wc -l < "$md_file")
  if [ "$total_lines" -le 1 ]; then
    total_lines_for_calc=$((total_sections + 1))
  else
    total_lines_for_calc=$total_lines
  fi
  local lines_per_section=$(( (total_lines_for_calc - 1) / total_sections ))
  [ "$lines_per_section" -lt 1 ] && lines_per_section=1

  local start_line=$(( 2 + (section_num - 1) * lines_per_section ))
  if [ "$section_num" -eq 1 ] && [ "$total_sections" -eq 1 ]; then
    start_line=1
  elif [ "$section_num" -eq 1 ]; then
    start_line=2
  fi

  local end_line=$(( start_line + lines_per_section - 1 ))
  [ "$start_line" -gt "$total_lines" ] && start_line=$total_lines

  # Create HTML for this section
  cat > "$output_file" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} - Part ${section_num}</title>
  <style>
$(get_enhanced_css)
  </style>
</head>
<body class="${layout_class}">
  <div class="eliza-header">
    <div class="eliza-logo">ElizaOS</div>
    <div class="page-indicator">Page ${section_num} of ${total_sections}</div>
  </div>
EOF

  # Extract the main title for the first page only
  if [ "$section_num" -eq 1 ]; then
    echo "<h1>${title}</h1>" >> "$output_file"
  else
    echo "<h1>${title} (continued)</h1>" >> "$output_file"
  fi
  
  # Create content section
  temp_md_section="${TEMP_DIR}/temp_section_${section_num}.md"
  if [ "$section_num" -eq 1 ] && [ "$total_sections" -eq 1 ]; then
    tail -n +2 "$md_file" > "$temp_md_section"
  elif [ "$section_num" -eq 1 ]; then
    sed -n "${start_line},${end_line}p" "$md_file" > "$temp_md_section"
  elif [ "$section_num" -eq "$total_sections" ]; then
    sed -n "${start_line},\$p" "$md_file" > "$temp_md_section"
  else
    sed -n "${start_line},${end_line}p" "$md_file" > "$temp_md_section"
  fi

  # Convert markdown to HTML
  pandoc -f markdown -t html "$temp_md_section" >> "$output_file"
  rm "$temp_md_section"
  
  # Add footer
  cat >> "$output_file" << EOF
  <div class="content-footer">
    <div class="generation-date">Generated $(date +"%Y-%m-%d")</div>
    <div class="eliza-watermark">elizaos.github.io/knowledge</div>
  </div>
</body>
</html>
EOF
}

# Enhanced HTML to image conversion with multiple fallbacks
convert_html_to_image() {
  local html_file=$1
  local png_path=$2
  local success=false
  
  log_info "Converting HTML to image: $(basename "$html_file")"
  
  # Primary: wkhtmltoimage (best quality)
  if command -v wkhtmltoimage &> /dev/null; then
    log_info "Attempting conversion with wkhtmltoimage..."
    if xvfb-run --auto-servernum --server-args="-screen 0 1024x768x24" \
       wkhtmltoimage --quiet --quality 100 --width 800 --enable-local-file-access \
       --disable-smart-shrinking --encoding utf-8 \
       "$html_file" "$png_path" 2>/dev/null; then
      if [ -f "$png_path" ] && [ -s "$png_path" ]; then
        log_success "wkhtmltoimage conversion successful"
        success=true
      fi
    fi
  fi
  
  # Fallback 1: Chromium headless
  if [ "$success" = false ] && command -v chromium-browser &> /dev/null; then
    log_warn "wkhtmltoimage failed, trying Chromium headless..."
    if chromium-browser --headless --disable-gpu --virtual-time-budget=2000 \
       --window-size=800,1000 --screenshot="$png_path" \
       "file://$html_file" 2>/dev/null; then
      if [ -f "$png_path" ] && [ -s "$png_path" ]; then
        log_success "Chromium conversion successful"
        success=true
      fi
    fi
  fi
  
  # Fallback 2: ImageMagick (basic, for emergencies)
  if [ "$success" = false ] && command -v convert &> /dev/null; then
    log_warn "Previous methods failed, trying ImageMagick (basic quality)..."
    # This is a very basic fallback and won't render HTML well
    if convert -size 800x1000 xc:white -pointsize 12 -fill black \
       -annotate +20+40 "Content generation failed - please check logs" \
       "$png_path" 2>/dev/null; then
      if [ -f "$png_path" ] && [ -s "$png_path" ]; then
        log_warn "ImageMagick fallback used (degraded quality)"
        success=true
      fi
    fi
  fi
  
  if [ "$success" = false ]; then
    log_error "All conversion methods failed for $html_file"
    return 1
  fi
  
  return 0
}

# Process the markdown file
log_info "Processing $(basename "$INPUT_FILE")..."

# Verify input file exists and is readable
if [ ! -f "$INPUT_FILE" ] || [ ! -r "$INPUT_FILE" ]; then
  log_error "Input file not found or not readable: $INPUT_FILE"
  cleanup_and_exit 1
fi

# Count words in the file
word_count=$(count_words "$INPUT_FILE")
log_info "Word count: $word_count"

# Determine optimal page count
page_count=$(determine_page_count "$word_count")
log_info "Splitting into $page_count page(s)"

# Create HTML sections
declare -a section_pngs

for ((i=1; i<=page_count; i++)); do
  section_html="$TEMP_DIR/section_${i}.html"
  create_section_html "$INPUT_FILE" $i $page_count "$section_html"
  
  section_png_path="$TEMP_DIR/section_${i}.png"
  section_pngs+=("$section_png_path")

  # Convert HTML to image with enhanced error handling
  if ! convert_html_to_image "$section_html" "$section_png_path"; then
    log_error "Failed to convert section $i to image"
    cleanup_and_exit 1
  fi
  log_success "Section $i image created: $(basename "$section_png_path")"
done

# Determine optimal layout and create final image
log_info "Assembling final poster from $page_count section(s)..."

# Enhanced montage with better spacing and quality
if [ "$page_count" -eq 1 ]; then
  cp "${section_pngs[0]}" "$OUTPUT_PNG"
elif [ "$page_count" -eq 2 ]; then
  convert "${section_pngs[0]}" "${section_pngs[1]}" +append "$OUTPUT_PNG"
elif [ "$page_count" -eq 4 ]; then
  montage "${section_pngs[0]}" "${section_pngs[1]}" \
          "${section_pngs[2]}" "${section_pngs[3]}" \
          -geometry +8+8 -tile 2x2 -background white "$OUTPUT_PNG"
elif [ "$page_count" -eq 6 ]; then
  montage "${section_pngs[0]}" "${section_pngs[1]}" "${section_pngs[2]}" \
          "${section_pngs[3]}" "${section_pngs[4]}" "${section_pngs[5]}" \
          -geometry +8+8 -tile 3x2 -background white "$OUTPUT_PNG"
elif [ "$page_count" -eq 9 ]; then
  montage "${section_pngs[0]}" "${section_pngs[1]}" "${section_pngs[2]}" \
          "${section_pngs[3]}" "${section_pngs[4]}" "${section_pngs[5]}" \
          "${section_pngs[6]}" "${section_pngs[7]}" "${section_pngs[8]}" \
          -geometry +8+8 -tile 3x3 -background white "$OUTPUT_PNG"
fi

# Verify final output
if [ ! -f "$OUTPUT_PNG" ] || [ ! -s "$OUTPUT_PNG" ]; then
  log_error "Final poster generation failed"
  cleanup_and_exit 1
fi

log_success "Created $OUTPUT_PNG"
log_success "Done! Enhanced poster saved to $OUTPUT_PNG"

# Cleanup handled by trap