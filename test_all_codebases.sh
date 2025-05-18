#!/bin/bash

set -eo pipefail
set -x

# Check if API is running
check_api() {
    if ! curl -s http://localhost:3003/upload_code > /dev/null; then
        echo "Error: API is not running on port 3003"
        echo "Please start the API server first with: python3 api.py"
        exit 1
    fi
}

# Function to test a codebase
test_codebase() {
    local codebase=$1
    echo "Testing codebase: $codebase"
    echo "----------------------------------------"
    
    # Clean up any existing zip file
    rm -f "${codebase}.zip"
    
    # Create zip file
    echo "Creating zip file from $codebase..."
    zip -r "${codebase}.zip" "$codebase"
    
    # Upload code
    echo "Uploading code to API..."
    response=$(curl -s -X POST -F "file=@${codebase}.zip" http://localhost:3003/upload_code)
    
    # Check for error in response
    if echo "$response" | grep -q '"error"'; then
        error_msg=$(echo "$response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo "Failed to upload code: $error_msg"
        return 1
    fi
    
    # Extract code_id using python for more reliable JSON parsing
    code_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['code_id'])")
    
    if [ -z "$code_id" ]; then
        echo "Failed to upload code: No code ID received"
        echo "API Response: $response"
        return 1
    fi
    
    echo "Code ID: $code_id"
    
    # Get call graph
    echo "Getting call graph..."
    graph_response=$(curl -s "http://localhost:3003/call_graph/$code_id")
    
    # Check for error in call graph response
    if echo "$graph_response" | grep -q '"error"'; then
        error_msg=$(echo "$graph_response" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo "Failed to get call graph: $error_msg"
        return 1
    fi
    
    # Save and display the response
    if [ -n "$graph_response" ]; then
        echo "$graph_response" | python3 -m json.tool > "${codebase}_results.json"
        echo "Raw response from call graph endpoint:"
        echo "----------------------------------------"
        cat "${codebase}_results.json"
        echo "----------------------------------------"
    else
        echo "Warning: Empty response from call graph endpoint"
        echo "{}" > "${codebase}_results.json"
    fi
    
    # Clean up
    rm "${codebase}.zip"
    echo ""
}

# Function to test joern_analyzer.py directly
test_joern_analyzer() {
    local codebase=$1
    echo "Testing joern_analyzer.py on: $codebase"
    echo "----------------------------------------"
    
    # Run joern_analyzer.py directly on the directory
    echo "Running joern_analyzer.py..."
    if ! python3 joern_analyzer.py "$codebase"; then
        echo "Error: joern_analyzer.py failed for $codebase"
        return 1
    fi
    echo "Analysis completed successfully"
    echo ""
}

# Check API availability before starting tests
check_api

# Test all codebases
echo "Starting tests for all codebases..."
echo "========================================"

# Test via API
echo "Testing via API..."
echo "----------------------------------------"
test_codebase "test_code/simple"
test_codebase "test_code/complex"
test_codebase "test_code/more_complex"

# Test via joern_analyzer.py directly
echo "Testing via joern_analyzer.py directly..."
echo "----------------------------------------"
test_joern_analyzer "test_code/simple"
test_joern_analyzer "test_code/complex"
test_joern_analyzer "test_code/more_complex"

echo "All tests completed!" 