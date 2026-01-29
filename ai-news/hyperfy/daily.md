# Hyperfy Discord - 2026-01-27

## Overall Discussion Highlights

### V1 to V2 Data Conversion
- Jin developed a comprehensive converter tool for Hyperfy worlds that outputs both V1 archived data and V2-ready files
- The converter packages everything together with the conversion script itself
- Output structure includes V2 folders containing db.sqlite, collections, and assets, alongside the original V1 data
- Including V2 files adds only about 270kb per world, which is minimal compared to overall zip sizes
- The tool creates a structured output that preserves original data while making it ready for V2 compatibility

### Technical File Handling
- Discussion about challenges with sharing .hyp files on Discord and GitHub
- Binary formats were noted as problematic for LLM understanding and security
- Git LFS was mentioned as a solution for handling binary files in repositories, though it requires payment info on GitHub

### Feature Development
- Jin reported successfully porting Hyperfy sky presets
- Work in progress on hyperfy-vrm for in-world avatar changing, though this may require additional technical assistance

## Key Questions & Answers

**Q: What does the converter output?** (asked by ash)  
**A:** A structured folder with V2 format files (db.sqlite, collections, assets), V1 archived data, README.txt, manifest.json, and the converter script itself (answered by jin)

**Q: How are .hyp files handled in git?** (asked by jin)  
**A:** They're binary files that would require Git LFS (answered by ash)

## Community Help & Collaboration

### Binary File Handling in Git
- **Helper:** ash
- **Helpee:** jin
- **Context:** Discussing how to handle .hyp binary files in git repositories
- **Resolution:** Ash suggested using Git LFS, though Jin noted this requires payment information on GitHub

### V1-V2 Converter Explanation
- **Helper:** jin
- **Helpee:** ash
- **Context:** Explaining the structure and functionality of the V1 to V2 converter
- **Resolution:** Jin provided detailed folder structure output and explained the included Python script for conversion

## Action Items

### Technical
- Coordinate implementation of V1 data exporter on the website (mentioned by jin)
- Complete hyperfy-vrm implementation for in-world avatar changing (mentioned by jin)
- Consider developing a scraper for non-Hyperfy hosted assets (mentioned by jin)
- Publish repository for the V1-V2 converter (mentioned by jin)

### Documentation
- Update documentation based on Discord analysis of .hyp files (mentioned by jin)