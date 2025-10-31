# archive_simple.py - IMPROVED VERSION
import os
import zipfile
import datetime
from pathlib import Path

def find_workspace_root():
    """Automatically find which workspace we're in"""
    possible_roots = [
        r"C:\Projects\GitHub_Active\Universal"
        r"C:\Projects\GitHub_Active\Modules",
        r"C:\Projects\GitHub_Active\ModulesModel\___Structured_Product_Modeling\Github_Utilities\Modules"

    ]
    
    current_dir = Path.cwd()
    
    for root in possible_roots:
        root_path = Path(root)
        try:
            if root_path.exists() and root_path in current_dir.parents:
                return root_path
        except:
            continue
    
    return current_dir

def archive_workspace():
    """Simple one-click archive of current workspace"""
    workspace_root = find_workspace_root()
    print(f"📁 Detected workspace: {workspace_root}")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # archive_name = f"workspace_backup_{timestamp}.zip"
    archive_name = f"Universal_WSbackup_{timestamp}.zip" 
    archives_dir = workspace_root.parent / "Archives"
    archives_dir.mkdir(exist_ok=True)
    archive_path = archives_dir / archive_name
    
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in workspace_root.rglob('*'):
            if ('__pycache__' not in str(file_path) and 
                '.pyc' not in str(file_path) and
                'Archives' not in str(file_path)):
                arcname = file_path.relative_to(workspace_root.parent)
                zipf.write(file_path, arcname)
    
    print(f"✅ Workspace archived: {archive_path}")
    return archive_path

def list_all_archives():
    """Show ALL archives with numbers for selection"""
    workspace_root = find_workspace_root()
    archives_dir = workspace_root.parent / "Archives"
    
    if not archives_dir.exists():
        print("❌ No archives found")
        return []
    
    archives = sorted(archives_dir.glob("*.zip"), key=os.path.getmtime, reverse=True)
    
    print("📚 All available archives:")
    print("-" * 60)
    for i, arch in enumerate(archives, 1):
        mod_time = datetime.datetime.fromtimestamp(arch.stat().st_mtime)
        size_mb = arch.stat().st_size / 1024 / 1024
        print(f"  {i:2d}. {arch.name}")
        print(f"      📅 {mod_time.strftime('%Y-%m-%d %H:%M')} | 📦 {size_mb:.1f} MB")
    
    return archives

def restore_any_archive():
    """Let user choose ANY archive to restore"""
    archives = list_all_archives()
    
    if not archives:
        return
    
    try:
        choice = input(f"\n🔄 Enter archive number to restore (1-{len(archives)}): ").strip()
        if not choice:
            return
            
        archive_number = int(choice)
        if 1 <= archive_number <= len(archives):
            selected_archive = archives[archive_number - 1]
            _restore_single_archive(selected_archive)
        else:
            print("❌ Invalid archive number")
            
    except ValueError:
        print("❌ Please enter a valid number")

def _restore_single_archive(archive_path):
    """Restore a specific archive to test folder"""
    # Create test folder with archive name
    test_dir = archive_path.parent / f"TEST_{archive_path.stem}"
    
    # Clear existing test directory
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(exist_ok=True)
    
    # Extract archive
    with zipfile.ZipFile(archive_path, 'r') as zipf:
        zipf.extractall(test_dir)
    
    print(f"✅ Restored to: {test_dir}")
    print(f"🚀 To test this version:")
    print(f"   cd \"{test_dir}\"")
    print(f"   python m_scanner_gui.py")

def delete_old_archives():
    """Optional: Clean up old archives (keep last 10)"""
    workspace_root = find_workspace_root()
    archives_dir = workspace_root.parent / "Archives"
    
    if not archives_dir.exists():
        return
    
    archives = sorted(archives_dir.glob("*.zip"), key=os.path.getmtime, reverse=True)
    
    if len(archives) > 10:
        print("🗑️  Cleaning up old archives (keeping last 10)...")
        for arch in archives[10:]:
            print(f"   Deleting: {arch.name}")
            arch.unlink()

if __name__ == "__main__":
    print("🔄 Workspace Archive Manager")
    print("=" * 50)
    
    workspace_root = find_workspace_root()
    print(f"📍 Current workspace: {workspace_root}")
    
    # Simple menu
    print("\nOptions:")
    print("1. 📦 Archive current workspace (quick backup)")
    print("2. 📚 Browse all archives")
    print("3. 🔄 Restore any archive")
    print("4. 🗑️  Clean up old archives (keep last 10)")
    
    try:
        choice = input("\nChoose (1-4, Enter=Archive): ").strip()
        
        if choice == "2":
            list_all_archives()
        elif choice == "3":
            restore_any_archive()
        elif choice == "4":
            delete_old_archives()
        else:  # Default: archive
            archive_workspace()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")