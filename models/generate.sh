#!/bin/bash

# Script to generate Pydantic models from JSON schema files
# Preserves directory hierarchy and creates __init__.py files

# Install datamodel-codegen if not already installed
if ! command -v datamodel-codegen &> /dev/null; then
    echo "🔧 Installing datamodel-codegen..."
    pip install datamodel-codegen
fi

set -e

# Base directories
MODELS_DIR="$(dirname "$0")"
OUTPUT_DIR="../pyDataverse/models"

echo "🚀 Starting model generation..."
echo "Models directory: $MODELS_DIR"
echo "Output directory: $OUTPUT_DIR"

# Clean up existing generated models (but preserve __init__.py structure)
echo "🧹 Cleaning up existing models..."
find "$OUTPUT_DIR" -name "*.py" -not -name "__init__.py" -delete 2>/dev/null || true

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Function to create __init__.py file with imports (only for leaf directories)
create_init_file() {
    local dir="$1"
    local init_file="$dir/__init__.py"
    
    echo "📝 Creating $init_file"
    
    # Start building the __init__.py content
    cat > "$init_file" << 'EOF'
"""
Auto-generated models from JSON schemas.
"""
EOF
    
    # Check if this directory has Python files (leaf directory)
    local py_files_count=$(find "$dir" -maxdepth 1 -name "*.py" -not -name "__init__.py" -type f | wc -l)
    
    # Only add imports and __all__ for leaf directories that contain Python files
    if [[ $py_files_count -gt 0 ]]; then
        # Arrays to collect imports and exports
        local -a module_imports=()
        local -a all_exports=()
        
        # Find all Python files in this directory (excluding __init__.py)
        while IFS= read -r -d '' py_file; do
            if [[ "$(basename "$py_file")" != "__init__.py" ]]; then
                local module_name=$(basename "$py_file" .py)
                
                # Get all class names from the Python file
                local class_names=$(grep -E "^class [A-Za-z][A-Za-z0-9_]*" "$py_file" 2>/dev/null | sed -E 's/^class ([A-Za-z][A-Za-z0-9_]*).*/\1/' | sort -u)
                
                if [[ -n "$class_names" ]]; then
                    # Create import statement
                    local classes_list=$(echo "$class_names" | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')
                    module_imports+=("from .$module_name import $classes_list")
                    
                    # Add classes to __all__ exports
                    while IFS= read -r class_name; do
                        [[ -n "$class_name" ]] && all_exports+=("\"$class_name\"")
                    done <<< "$class_names"
                fi
            fi
        done < <(find "$dir" -maxdepth 1 -name "*.py" -type f -print0)
        
        # Write imports to file if any exist
        if [[ ${#module_imports[@]} -gt 0 ]]; then
            echo "" >> "$init_file"
            printf '%s\n' "${module_imports[@]}" >> "$init_file"
        fi
        
        # Write __all__ declaration if any exports exist
        if [[ ${#all_exports[@]} -gt 0 ]]; then
            echo "" >> "$init_file"
            echo "__all__ = [" >> "$init_file"
            
            # Sort and write exports
            printf '%s\n' "${all_exports[@]}" | sort -u | while read -r export; do
                echo "    $export," >> "$init_file"
            done
            
            echo "]" >> "$init_file"
        fi
    fi
}

# Function to generate model from JSON schema
generate_model() {
    local json_file="$1"
    local relative_path="$2"
    
    # Calculate output directory and file paths
    local dir_path=$(dirname "$relative_path")
    # Remove leading ./ if present
    if [[ "$dir_path" == "." ]]; then
        local output_subdir="$OUTPUT_DIR"
    else
        local output_subdir="$OUTPUT_DIR/$dir_path"
    fi
    local base_name=$(basename "$json_file" .json)
    # Replace hyphens with underscores for valid Python module names
    local python_name="${base_name//-/_}"
    local output_file="$output_subdir/${python_name}.py"
    
    echo "🔧 Processing: $json_file -> $output_file"
    
    # Create output subdirectory
    mkdir -p "$output_subdir"
    
    # Generate the model
    datamodel-codegen \
        --input "$json_file" \
        --input-file-type jsonschema \
        --output "$output_file" \
        --output-model-type pydantic_v2.BaseModel \
        --use-schema-description \
        --use-field-description \
        --allow-population-by-field-name \
        --snake-case-field \
        --reuse-model \
        --use-annotated \
        --field-constraints \
        --enable-version-header \
        --target-python-version 3.9 \
        --enum-field-as-literal all \
        --collapse-root-models
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Successfully generated: $output_file"
    else
        echo "❌ Failed to generate: $output_file"
        return 1
    fi
}

# Find all JSON files and process them
echo "🔍 Finding JSON schema files..."
processed_count=0

# Process JSON files, excluding generate.sh
while IFS= read -r -d '' json_file; do
    # Get relative path from models directory
    relative_path="${json_file#$MODELS_DIR/}"
    
    # Skip if it's the generate.sh script itself
    if [[ "$json_file" == *"generate.sh"* ]]; then
        continue
    fi
    
    generate_model "$json_file" "$relative_path"
    ((processed_count++))
    
done < <(find "$MODELS_DIR" -name "*.json" -type f -print0)

# Create __init__.py files for all directories (bottom-up to handle dependencies)
echo "📁 Creating __init__.py files..."

# First, collect all directories and sort by depth (deepest first)
directories=()
while IFS= read -r -d '' dir; do
    if [[ "$dir" != "$MODELS_DIR" ]]; then
        relative_dir="${dir#$MODELS_DIR/}"
        output_subdir="$OUTPUT_DIR/$relative_dir"
        
        if [[ -d "$output_subdir" ]]; then
            directories+=("$output_subdir")
        fi
    fi
done < <(find "$MODELS_DIR" -type d -print0)

# Sort directories by depth (deepest first) to ensure subdirectories are processed before parents
IFS=$'\n' sorted_dirs=($(printf '%s\n' "${directories[@]}" | awk '{print NF-1 " " $0}' FS='/' | sort -nr | cut -d' ' -f2-))

# Create __init__.py files in order
for dir in "${sorted_dirs[@]}"; do
    create_init_file "$dir"
done

# Keep root __init__.py simple as requested
echo "📝 Keeping root __init__.py simple"
cat > "$OUTPUT_DIR/__init__.py" << 'EOF'
"""
Auto-generated models from JSON schemas.
"""
EOF

echo "🎉 Model generation complete!"
echo "📊 Processed $processed_count JSON schema files"
echo "📂 Generated models in: $OUTPUT_DIR"

# List generated structure
echo ""
echo "📋 Generated structure:"
find "$OUTPUT_DIR" -type f -name "*.py" | sort
