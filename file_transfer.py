#!/usr/bin/env python3
"""
Interactive File Transfer with Overwrite Protection
Transfer files from Analysis to UScan workspace
"""

import os
import shutil
import sys
from pathlib import Path
import fnmatch

class FileTransfer:
    def __init__(self):
        self.source_dir = Path(r"C:\Projects\GitHub_Active\Analysis")
        self.dest_dir = Path(r"C:\Projects\GitHub_Active\Universal\UScan")
        
        # File patterns to look for
        self.file_patterns = [
            "*.py", "*.json", "*.txt", "*.md", 
            "*.yaml", "*.yml", "*.toml", "*.ini",
            "*.csv", "*.html", "*.js", "*.css"
        ]
        
        self.transferred_files = []
        self.skipped_files = []
        self.overwritten_files = []

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        """Display application header"""
        print("🔄 USCAN FILE TRANSFER UTILITY")
        print("=" * 50)
        print(f"Source:      {self.source_dir}")
        print(f"Destination: {self.dest_dir}")
        print("=" * 50)

    def find_files(self):
        """Find all matching files in source directory"""
        all_files = []
        
        for pattern in self.file_patterns:
            for file_path in self.source_dir.rglob(pattern):
                if file_path.is_file():
                    # Get relative path for better display
                    try:
                        rel_path = file_path.relative_to(self.source_dir)
                    except ValueError:
                        rel_path = file_path
                    
                    all_files.append({
                        'path': file_path,
                        'relative_path': rel_path,
                        'size': file_path.stat().st_size,
                        'modified': file_path.stat().st_mtime
                    })
        
        return sorted(all_files, key=lambda x: x['relative_path'])

    def format_file_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def format_timestamp(self, timestamp):
        """Format timestamp for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

    def display_files(self, files):
        """Display files with selection numbers"""
        print(f"\n📁 Found {len(files)} files:")
        print("-" * 80)
        print(f"{'#':<3} {'File':<40} {'Size':<10} {'Modified':<16} {'Status':<10}")
        print("-" * 80)
        
        for i, file_info in enumerate(files, 1):
            rel_path = str(file_info['relative_path'])
            if len(rel_path) > 38:
                rel_path = rel_path[:35] + "..."
            
            size = self.format_file_size(file_info['size'])
            modified = self.format_timestamp(file_info['modified'])
            
            # Check if file already exists in destination
            dest_path = self.dest_dir / file_info['relative_path']
            status = "EXISTS" if dest_path.exists() else "NEW"
            
            print(f"{i:<3} {rel_path:<40} {size:<10} {modified:<16} {status:<10}")

    def get_user_selection(self, files):
        """Get file selection from user"""
        while True:
            try:
                print(f"\nSelect files to transfer (1-{len(files)})")
                print("Options:")
                print("  - Single number: 5")
                print("  - Range: 1-10")
                print("  - Multiple: 1,3,5")
                print("  - All: all")
                print("  - Cancel: 0")
                
                choice = input("\nEnter your choice: ").strip().lower()
                
                if choice == '0':
                    return None
                elif choice == 'all':
                    return list(range(len(files)))
                elif '-' in choice:
                    # Range selection (e.g., "1-5")
                    start, end = map(int, choice.split('-'))
                    return list(range(start-1, end))
                elif ',' in choice:
                    # Multiple selection (e.g., "1,3,5")
                    return [int(x.strip())-1 for x in choice.split(',')]
                else:
                    # Single selection
                    return [int(choice)-1]
                    
            except (ValueError, IndexError):
                print("❌ Invalid selection. Please try again.")
            except KeyboardInterrupt:
                print("\n\n⚠️  Transfer cancelled by user.")
                return None

    def confirm_overwrite(self, source_file, dest_file):
        """Ask user confirmation for overwriting files"""
        print(f"\n⚠️  File already exists: {dest_file.name}")
        print(f"   Source: {self.format_timestamp(source_file.stat().st_mtime)}")
        print(f"   Destination: {self.format_timestamp(dest_file.stat().st_mtime)}")
        
        while True:
            choice = input("Overwrite? (y/n/a/s): ").strip().lower()
            if choice in ['y', 'yes']:
                return 'overwrite'
            elif choice in ['n', 'no']:
                return 'skip'
            elif choice in ['a', 'all']:
                return 'overwrite_all'
            elif choice in ['s', 'skip_all']:
                return 'skip_all'
            else:
                print("Please enter y(es), n(o), a(ll), or s(kip all)")

    def transfer_file(self, file_info, overwrite_mode='ask'):
        """Transfer a single file with overwrite protection"""
        source_path = file_info['path']
        dest_path = self.dest_dir / file_info['relative_path']
        
        # Create destination directory if it doesn't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists
        if dest_path.exists():
            if overwrite_mode == 'ask':
                action = self.confirm_overwrite(source_path, dest_path)
                if action == 'skip':
                    self.skipped_files.append(file_info)
                    return 'skipped'
                elif action == 'skip_all':
                    self.skipped_files.append(file_info)
                    return 'skip_all'
                elif action == 'overwrite_all':
                    overwrite_mode = 'overwrite_all'
            
            if overwrite_mode in ['overwrite', 'overwrite_all']:
                shutil.copy2(source_path, dest_path)
                self.overwritten_files.append(file_info)
                return 'overwritten'
            else:
                self.skipped_files.append(file_info)
                return 'skipped'
        else:
            # New file
            shutil.copy2(source_path, dest_path)
            self.transferred_files.append(file_info)
            return 'transferred'

    def show_summary(self):
        """Display transfer summary"""
        print("\n" + "=" * 50)
        print("📊 TRANSFER SUMMARY")
        print("=" * 50)
        
        if self.transferred_files:
            print(f"✅ Transferred ({len(self.transferred_files)}):")
            for file in self.transferred_files:
                print(f"   📄 {file['relative_path']}")
        
        if self.overwritten_files:
            print(f"🔄 Overwritten ({len(self.overwritten_files)}):")
            for file in self.overwritten_files:
                print(f"   📄 {file['relative_path']}")
        
        if self.skipped_files:
            print(f"⏭️  Skipped ({len(self.skipped_files)}):")
            for file in self.skipped_files:
                print(f"   📄 {file['relative_path']}")
        
        total = len(self.transferred_files) + len(self.overwritten_files) + len(self.skipped_files)
        print(f"\n🎯 Total processed: {total} files")

    def run(self):
        """Main application loop"""
        try:
            self.clear_screen()
            self.display_header()
            
            # Find files
            files = self.find_files()
            
            if not files:
                print("❌ No matching files found in source directory.")
                return
            
            # Display files
            self.display_files(files)
            
            # Get user selection
            selected_indices = self.get_user_selection(files)
            
            if selected_indices is None:
                print("Transfer cancelled.")
                return
            
            # Transfer selected files
            selected_files = [files[i] for i in selected_indices]
            overwrite_mode = 'ask'
            
            print(f"\n🔄 Transferring {len(selected_files)} files...")
            
            for file_info in selected_files:
                result = self.transfer_file(file_info, overwrite_mode)
                
                if result == 'skip_all':
                    overwrite_mode = 'skip'
                    print("⏭️  Skipping all remaining existing files...")
                elif result == 'overwritten':
                    print(f"🔄 Overwritten: {file_info['relative_path']}")
                elif result == 'transferred':
                    print(f"✅ Transferred: {file_info['relative_path']}")
                elif result == 'skipped':
                    print(f"⏭️  Skipped: {file_info['relative_path']}")
            
            # Show summary
            self.show_summary()
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Transfer cancelled by user.")
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Main function"""
    transfer = FileTransfer()
    transfer.run()

if __name__ == "__main__":
    main()