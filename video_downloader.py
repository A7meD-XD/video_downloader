#!/usr/bin/env python3
"""
Social Media Video Downloader
A professional CLI tool for downloading videos from multiple platforms

Author: Your Name
License: MIT
Repository: https://github.com/yourusername/video-downloader
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

try:
    import yt_dlp
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.table import Table
    from rich import box
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn, TransferSpeedColumn
    from rich.tree import Tree
    from rich.align import Align
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
except ImportError:
    print("⚠️  Missing required libraries. Please install them:")
    print("pip install -r requirements.txt")
    sys.exit(1)


console = Console()


@dataclass
class PlatformConfig:
    """Configuration for each social media platform"""
    name: str
    icon: str
    examples: List[str]
    domains: List[str]
    format_preference: str = 'best'


class Platform:
    """Platform definitions and configurations"""
    
    YOUTUBE = PlatformConfig(
        name="YouTube",
        icon="🎬",
        domains=["youtube.com", "youtu.be"],
        examples=[
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/xxxxxxxxxxx"
        ],
        format_preference="bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    )
    
    INSTAGRAM = PlatformConfig(
        name="Instagram",
        icon="📸",
        domains=["instagram.com"],
        examples=[
            "https://www.instagram.com/reel/CxxxxxXXXXX/",
            "https://www.instagram.com/p/CxxxxxXXXXX/",
            "https://www.instagram.com/tv/CxxxxxXXXXX/"
        ]
    )
    
    FACEBOOK = PlatformConfig(
        name="Facebook",
        icon="👥",
        domains=["facebook.com", "fb.watch"],
        examples=[
            "https://www.facebook.com/watch?v=1234567890",
            "https://fb.watch/xxxxxxxxxxx/",
            "https://www.facebook.com/username/videos/1234567890"
        ]
    )
    
    TWITTER = PlatformConfig(
        name="Twitter/X",
        icon="🐦",
        domains=["twitter.com", "x.com"],
        examples=[
            "https://twitter.com/username/status/1234567890",
            "https://x.com/username/status/1234567890"
        ]
    )
    
    PINTEREST = PlatformConfig(
        name="Pinterest",
        icon="📌",
        domains=["pinterest.com"],
        examples=[
            "https://www.pinterest.com/pin/1234567890/"
        ]
    )
    
    @classmethod
    def get_all(cls) -> Dict[str, PlatformConfig]:
        """Get all platform configurations"""
        return {
            '1': cls.YOUTUBE,
            '2': cls.INSTAGRAM,
            '3': cls.FACEBOOK,
            '4': cls.TWITTER,
            '5': cls.PINTEREST
        }
    
    @classmethod
    def detect_platform(cls, url: str) -> Optional[PlatformConfig]:
        """Auto-detect platform from URL"""
        for platform in cls.get_all().values():
            if any(domain in url.lower() for domain in platform.domains):
                return platform
        return None


class UIManager:
    """Manages all UI elements and displays"""
    
    def __init__(self, console: Console):
        self.console = console
    
    def show_banner(self):
        """Display animated welcome banner"""
        banner_text = Text()
        banner_text.append("\n")
        banner_text.append("╔═══════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner_text.append("║                                                               ║\n", style="bold cyan")
        banner_text.append("║           ", style="bold cyan")
        banner_text.append("🎥  SOCIAL MEDIA VIDEO DOWNLOADER  🎥", style="bold yellow blink")
        banner_text.append("           ║\n", style="bold cyan")
        banner_text.append("║                                                               ║\n", style="bold cyan")
        banner_text.append("║              ", style="bold cyan")
        banner_text.append("Download videos from 5+ platforms", style="bold white")
        banner_text.append("               ║\n", style="bold cyan")
        banner_text.append("║                    ", style="bold cyan")
        banner_text.append("Fast • Reliable • Easy", style="bold green")
        banner_text.append("                    ║\n", style="bold cyan")
        banner_text.append("║                                                               ║\n", style="bold cyan")
        banner_text.append("╚═══════════════════════════════════════════════════════════════╝\n", style="bold cyan")
        
        self.console.print(Align.center(banner_text))
    
    def show_platforms_menu(self, platforms: Dict[str, PlatformConfig]):
        """Display beautiful platforms menu"""
        table = Table(
            title="[bold yellow]📱 Supported Platforms[/bold yellow]",
            box=box.HEAVY,
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            title_style="bold yellow"
        )
        
        table.add_column("Option", style="bold cyan", justify="center", width=10)
        table.add_column("Platform", style="bold green", width=20)
        table.add_column("Icon", justify="center", width=8)
        table.add_column("Status", style="bold", width=15)
        
        for key, platform in platforms.items():
            table.add_row(
                key,
                platform.name,
                platform.icon,
                "[green]✓ Active[/green]"
            )
        
        table.add_row("", "", "", "", style="dim")
        table.add_row("0", "Exit Program", "🚪", "[red]Exit[/red]", style="bold red")
        
        self.console.print()
        self.console.print(Align.center(table))
    
    def show_platform_guide(self, platform: PlatformConfig):
        """Show detailed guide for selected platform"""
        tree = Tree(
            f"[bold cyan]{platform.icon} {platform.name} - URL Examples[/bold cyan]",
            guide_style="bold cyan"
        )
        
        for i, example in enumerate(platform.examples, 1):
            branch = tree.add(f"[yellow]Example {i}[/yellow]")
            branch.add(f"[white]{example}[/white]")
        
        tips = tree.add("[bold green]💡 Tips[/bold green]")
        tips.add("[white]• Copy URL directly from your browser[/white]")
        tips.add("[white]• Make sure the video is public[/white]")
        tips.add("[white]• Video will be saved in highest quality[/white]")
        
        panel = Panel(
            tree,
            title=f"[bold green]How to Download from {platform.name}[/bold green]",
            border_style="green",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
    
    def show_video_info(self, info: dict):
        """Display video information in a beautiful table"""
        table = Table(
            title="[bold yellow]📹 Video Information[/bold yellow]",
            box=box.DOUBLE_EDGE,
            show_header=False,
            border_style="yellow",
            title_style="bold yellow"
        )
        
        table.add_column("Property", style="bold cyan", width=20)
        table.add_column("Value", style="white", width=60)
        
        # Format duration
        duration = info.get('duration', 0)
        minutes, seconds = divmod(int(duration), 60)
        duration_str = f"{minutes}m {seconds}s" if duration else "N/A"
        
        # Format views
        views = info.get('view_count', 'N/A')
        if isinstance(views, int):
            views = f"{views:,}"
        
        # Format file size
        filesize = info.get('filesize', info.get('filesize_approx', 'N/A'))
        if isinstance(filesize, int):
            filesize_mb = filesize / (1024 * 1024)
            filesize = f"{filesize_mb:.2f} MB"
        
        table.add_row("📝 Title", info.get('title', 'N/A'))
        table.add_row("👤 Uploader", info.get('uploader', 'N/A'))
        table.add_row("⏱️  Duration", duration_str)
        table.add_row("👁️  Views", str(views))
        table.add_row("💾 File Size", str(filesize))
        table.add_row("📅 Upload Date", info.get('upload_date', 'N/A'))
        
        self.console.print()
        self.console.print(Align.center(table))
    
    def show_success_message(self, output_path: Path, filename: str):
        """Display success message with file info"""
        success_text = Text()
        success_text.append("✅ ", style="bold green")
        success_text.append("Download Completed Successfully!\n\n", style="bold green")
        success_text.append("📁 ", style="cyan")
        success_text.append("File Location:\n", style="bold cyan")
        success_text.append(f"   {output_path / filename}\n\n", style="white")
        success_text.append("🎉 ", style="yellow")
        success_text.append("Ready to watch!", style="bold yellow")
        
        panel = Panel(
            Align.center(success_text),
            border_style="bold green",
            box=box.DOUBLE,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
    
    def show_error_message(self, error: str):
        """Display error message with troubleshooting tips"""
        error_panel = Panel(
            f"[bold red]❌ Download Failed[/bold red]\n\n"
            f"[yellow]Error Details:[/yellow]\n{error}\n\n"
            f"[cyan]🔧 Troubleshooting Tips:[/cyan]\n"
            f"[white]• Verify the URL is correct and complete\n"
            f"• Check if the video is public and accessible\n"
            f"• Ensure you have stable internet connection\n"
            f"• Try updating yt-dlp: pip install -U yt-dlp\n"
            f"• Some platforms may require authentication[/white]",
            border_style="red",
            box=box.HEAVY,
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(error_panel)


class DownloadProgressHook:
    """Custom progress hook for yt-dlp"""
    
    def __init__(self, console: Console):
        self.console = console
        self.progress = None
        self.task = None
    
    def __call__(self, d):
        if d['status'] == 'downloading':
            if self.progress is None:
                self.progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[bold cyan]{task.description}"),
                    BarColumn(bar_width=40),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    console=self.console
                )
                self.progress.start()
                self.task = self.progress.add_task(
                    "Downloading...",
                    total=d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                )
            
            downloaded = d.get('downloaded_bytes', 0)
            self.progress.update(self.task, completed=downloaded)
        
        elif d['status'] == 'finished':
            if self.progress:
                self.progress.stop()
                self.progress = None


class VideoDownloader:
    """Main video downloader class with advanced features"""
    
    def __init__(self, output_dir: str = "downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.ui = UIManager(console)
        self.platforms = Platform.get_all()
        self.download_history: List[str] = []
    
    def configure_ydl_options(self, platform: PlatformConfig) -> dict:
        """Configure yt-dlp options based on platform"""
        progress_hook = DownloadProgressHook(console)
        
        options = {
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'format': platform.format_preference,
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [progress_hook],
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
        
        return options
    
    def download_video(self, url: str, platform: PlatformConfig) -> bool:
        """Download video with advanced error handling"""
        try:
            ydl_opts = self.configure_ydl_options(platform)
            
            with console.status(
                "[bold cyan]Fetching video information...",
                spinner="dots"
            ):
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
            
            # Show video info
            self.ui.show_video_info(info)
            console.print()
            
            # Confirm download
            if not Confirm.ask(
                "[bold yellow]⬇️  Proceed with download?[/bold yellow]",
                default=True
            ):
                console.print("[yellow]⚠️  Download cancelled by user[/yellow]")
                return False
            
            # Download video
            console.print()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Success message
            filename = ydl.prepare_filename(info)
            self.ui.show_success_message(self.output_dir, Path(filename).name)
            
            # Add to history
            self.download_history.append(info.get('title', 'Unknown'))
            
            return True
            
        except Exception as e:
            self.ui.show_error_message(str(e))
            return False
    
    def show_statistics(self):
        """Show download statistics"""
        if not self.download_history:
            return
        
        stats_table = Table(
            title="[bold cyan]📊 Download Statistics[/bold cyan]",
            box=box.ROUNDED,
            border_style="cyan"
        )
        
        stats_table.add_column("#", style="cyan", width=5)
        stats_table.add_column("Video Title", style="white", width=50)
        
        for i, title in enumerate(self.download_history, 1):
            stats_table.add_row(str(i), title[:47] + "..." if len(title) > 50 else title)
        
        console.print()
        console.print(stats_table)
    
    def run(self):
        """Main application loop"""
        self.ui.show_banner()
        
        while True:
            self.ui.show_platforms_menu(self.platforms)
            console.print()
            
            choice = Prompt.ask(
                "[bold cyan]🎯 Select a platform[/bold cyan]",
                choices=['0', '1', '2', '3', '4', '5'],
                default='1'
            )
            
            if choice == '0':
                if self.download_history:
                    self.show_statistics()
                console.print()
                console.print(Panel(
                    "[bold yellow]👋 Thank you for using Video Downloader!\n"
                    "⭐ If you like it, star us on GitHub![/bold yellow]",
                    border_style="yellow",
                    box=box.DOUBLE
                ))
                console.print()
                break
            
            platform = self.platforms[choice]
            self.ui.show_platform_guide(platform)
            console.print()
            
            url = Prompt.ask("[bold green]🔗 Enter video URL[/bold green]").strip()
            
            if not url:
                console.print("[red]❌ URL cannot be empty![/red]")
                continue
            
            # Validate URL
            detected_platform = Platform.detect_platform(url)
            if detected_platform and detected_platform.name != platform.name:
                console.print(
                    f"[yellow]⚠️  Warning: URL appears to be from {detected_platform.name}, "
                    f"not {platform.name}[/yellow]"
                )
                if not Confirm.ask("Continue anyway?", default=False):
                    continue
            
            console.print()
            self.download_video(url, platform)
            console.print()
            
            if not Confirm.ask(
                "[cyan]🔄 Download another video?[/cyan]",
                default=True
            ):
                if self.download_history:
                    self.show_statistics()
                console.print()
                console.print(Panel(
                    "[bold yellow]👋 Thank you for using Video Downloader!\n"
                    "⭐ If you like it, star us on GitHub![/bold yellow]",
                    border_style="yellow",
                    box=box.DOUBLE
                ))
                console.print()
                break


def main():
    """Entry point of the application"""
    try:
        downloader = VideoDownloader()
        downloader.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Operation cancelled by user. Goodbye![/yellow]\n")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]❌ Unexpected error: {str(e)}[/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()