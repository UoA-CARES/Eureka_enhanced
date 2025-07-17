import os
import argparse
import shutil

def is_coding_file(filename):
    """Check if a file is related to coding based on its extension."""
    # Extensions for various programming languages and coding-related files
    coding_extensions = {
        # Python
        '.py', '.pyc', '.pyd', '.pyo', '.pyw', '.ipynb',
        
        # C/C++
        '.c', '.cpp', '.cc', '.h', '.hpp', '.cxx', '.hxx',
        
        # Web Development
        '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx',
        '.php', '.asp', '.aspx', '.jsp', '.cshtml',
        
        # Java and JVM languages
        '.java', '.class', '.jar', '.kt', '.kts', '.scala', '.groovy',
        
        # C# and .NET
        '.cs', '.vb', '.fs', '.xaml', '.csproj', '.sln',
        
        # Mobile Development
        '.swift', '.m', '.mm', '.dart', '.kotlin',  # Note: .m is shared with MATLAB
        
        # Scientific/Technical Computing
        '.mat', '.fig', '.mlx', '.p', '.mlapp', '.mex*',  # MATLAB
        '.jl',  # Julia
        '.nb', '.wl', '.wls', '.m', # Mathematica/Wolfram
        '.npy', '.npz',  # NumPy
        '.oct', '.sci',  # Octave/Scilab
        '.sage',  # SageMath
        
        # Scripting
        '.sh', '.bash', '.zsh', '.ps1', '.bat', '.cmd', '.rb', '.perl', '.pl', '.pm',
        '.lua', '.tcl', '.r', '.rmd',
        
        # Systems Programming
        '.go', '.rs', '.asm', '.s',
        
        # Functional Languages
        '.hs', '.lhs', '.ml', '.mli', '.clj', '.cljs', '.ex', '.exs', '.erl', '.hrl',
        
        # Data/Config formats
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.csv',
        
        # Build/Config
        '.cmake', '.gradle', '.make', '.makefile', '.dockerfile',
        '.gitignore', '.editorconfig',
        
        # Documentation
        '.md', '.markdown', '.rst', '.adoc', '.tex',
        '.txt', '.org',
        
        # Other Languages
        '.f', '.f90', '.f95', '.for', '.lisp', '.scm', '.rkt', '.sql'
    }
    
    # Also consider files without extensions but with coding-related names
    coding_filenames = {
        'makefile', 'dockerfile', 'vagrantfile', 'jenkinsfile', 
        'rakefile', 'gemfile', 'procfile', 'brewfile'
    }
    
    # Check extensions
    _, ext = os.path.splitext(filename.lower())
    if ext in coding_extensions:
        return True
    
    # Check filenames
    if filename.lower() in coding_filenames:
        return True
        
    return False

def filter_non_coding_files(directory, dry_run=False, verbose=False):
    """Recursively delete files not related to coding in the given directory."""
    deleted_count = 0
    
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            
            if not is_coding_file(file):
                if verbose:
                    try:
                        print(f"{'Would delete' if dry_run else 'Deleting'}: {file_path}")
                    except UnicodeEncodeError:
                        # Handle filenames with invalid Unicode characters
                        safe_path = file_path.encode('utf-8', errors='replace').decode('utf-8')
                        print(f"{'Would delete' if dry_run else 'Deleting'}: {safe_path} (containing special characters)")
                
                if not dry_run:
                    try:
                        os.remove(file_path)
                    except (OSError, IOError) as e:
                        print(f"Error deleting file: {str(e)}")
                deleted_count += 1
    
    return deleted_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete files not relevant to coding')
    parser.add_argument('directory', nargs='?', default='.', help='Directory to scan (default: current directory)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed output')
    
    args = parser.parse_args()
    
    # Ensure the directory exists
    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a valid directory")
        exit(1)
    
    print(f"Scanning directory: {os.path.abspath(args.directory)}")
    
    if args.dry_run:
        print("DRY RUN MODE: No files will be deleted")
    
    # Confirm before proceeding
    if not args.dry_run:
        confirm = input("This will permanently delete files. Continue? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled")
            exit(0)
    
    # Process the directory
    deleted = filter_non_coding_files(args.directory, args.dry_run, args.verbose)
    
    print(f"{'Would delete' if args.dry_run else 'Deleted'} {deleted} non-coding files")
